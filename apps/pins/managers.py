import datetime
import random

from django.db import models
from django.db.models import Q
from django.db import connection, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.utils import translation
from django.core.cache import cache
from django.contrib.auth.models import User


from pins import CATEGORY_LIST_CACHE_KEY, USER_BOARDS_CACHE_KEY, CACHE_TIMEOUT
from pins.follow import follow

class BoardQuerySet(models.query.QuerySet):

	def annotate_with_pins(self, related_limit=9):
		from pins.models import Pin
		boards = list(self)
		board_pks = [b.pk for b in boards]
		board_pins = {}
		if len(board_pks)>0:
			one_pin_q = """(SELECT pins_pin.id, pins_pin.board_id, pins_pin.image, pins_pin.is_repin, pins_pin.source_pin_id,
                                T3.id AS source_pin_id, T3.image as source_pin_image FROM pins_pin
                                LEFT OUTER JOIN pins_pin T3 ON (pins_pin.source_pin_id = T3.id)
                                WHERE (pins_pin.board_id = %%d AND pins_pin.is_active = True )
                                ORDER BY pins_pin.id DESC LIMIT %d)""" % related_limit
			pin_queries = [one_pin_q % b.pk for b in boards]
			result_query = ' UNION ALL '.join(pin_queries)
			cursor = connection.cursor()
			cursor.execute(result_query)
			for r in cursor.fetchall():
				if not r[1] in board_pins:
					board_pins[r[1]]=[]
				board_pins[r[1]].append(Pin(pk=r[0], image=r[2], is_repin=r[3],
							source_pin=Pin(pk=r[5], image=r[6])))

		for b in boards:
			if b.pk in board_pins:
				b.pins = board_pins[b.pk]
			else:
				b.pins = []
		return boards

	def in_bulk(self, id_list):
		"""
		Returns a dictionary mapping each of the given IDs to the object with
		that ID.
		"""
		assert self.query.can_filter(), \
				"Cannot use 'limit' or 'offset' with in_bulk"
		assert isinstance(id_list, (tuple,  list, set, frozenset)), \
				"in_bulk() must be provided with a list of IDs."
		if not id_list:
			return {}
		qs = self.filter(pk__in = id_list).annotate_with_pins()
		return dict([(obj.pk, obj) for obj in qs])


class BoardManager(models.Manager):
	def get_query_set(self):
		return BoardQuerySet(self.model)

	def get_user_public_boards(self, user, related_limit=12):
		return self.filter(is_active=True, category__is_active=True, 
			user=user).select_related('category', 'user').order_by('-id').annotate_with_pins(related_limit=related_limit)

	def get_user_boards(self, user):
		if not hasattr(user,'pk'):
			pk = int(user)
		else:
			pk = user.pk
		boards = cache.get('%s_%d' % (USER_BOARDS_CACHE_KEY, pk))
		if not boards:
			boards = self.filter(is_active=True, category__is_active=True, user=pk).select_related()
			cache.set('%s_%d' % (USER_BOARDS_CACHE_KEY, pk), boards, CACHE_TIMEOUT)
		return boards

	def get_active_boards(self):
		return self.filter(is_active=True, category__is_active=True, user__is_active=True)

	class Meta:
		use_for_related_fields = True


class CategoryManager(models.Manager):
	def get_list_for_dropdown(self):
		"""
			Returns a queryset/list of categories which are shown in dropdown
		"""
		language = translation.get_language()
		categories = cache.get('%s_%s' % (CATEGORY_LIST_CACHE_KEY, language))
		if not categories:
			categories = self.filter(is_active=True).order_by('name')
			cache.set('%s_%s' % (CATEGORY_LIST_CACHE_KEY, language), categories, CACHE_TIMEOUT)

		return categories

	def get_list_for_welcome_screen(self):
		return self.filter(is_active=True, show_upon_signup=True).order_by('name')


class PinQuerySet(models.query.QuerySet):
	def annotate_with_comments(self, related_limit=3):
		"""
		Fetches latest %related_limit comments for each pin, in one query.
		This method evaluates queryset, so be careful to call it the last in chain- after filters and slicing.
		"""
		ctype = ContentType.objects.get_for_model(self.model)
		pin_pks = self.values_list('id', flat=True)
		if len(pin_pks)>0:
			base_query = "(SELECT c.*, u.username as user_username, u.first_name as user_first_name, u.last_name as user_last_name \
                          FROM django_comments c LEFT JOIN auth_user u ON u.id = c.user_id \
                          WHERE content_type_id=%d AND object_pk=%%d AND is_public=True AND is_removed=False ORDER by id DESC LIMIT %d)" % (ctype.pk, related_limit)
			comment_queries = [base_query % pk for pk in pin_pks]
			result_query = ' UNION ALL '.join(comment_queries)
			comments = list(Comment.objects.raw(result_query))
			pins = list(self)
			for p in pins:
				pin_comments = []
				for c in comments:
					if int(c.object_pk)==p.pk:
						c.user = User(username=c.user_username, first_name=c.user_first_name, last_name=c.user_last_name, pk=c.user_id)
						pin_comments.append(c)
				p.comments = pin_comments

			return pins
		else:
			return self

class PinManager(models.Manager):
	def get_query_set(self):
		return PinQuerySet(self.model)


	def latest_pins(self, category=None):
		qs = self.all().filter(video_id='', is_active=True, board__is_active=True,
			board__category__is_active=True).select_related('board', 'domain', 'board__category', 
				'source_pin','board__user','created_user')
		if category:
			qs = qs.filter(board__category=category)
		
		return qs

	def latest_video_pins(self):
		qs = self.active_pins()
		return qs.exclude(video_parser='', video_id='')

	def get_pin_count_by_url(self, url):
		return self.filter(is_active=True, board__is_active=True, board__category__is_active=True, original_image_url=url).count()

	def latest_pins_for_user(self, user, category=None):
		user = getattr(user,'pk', user)
		followed_users = follow.get_user_following(user)
		unfollowed_boards = follow.get_user_unfollowed_boards(user)
		followed_boards = follow.get_user_followed_boards(user)

		query_params = Q(video_id='') & Q(is_active=True) & Q(board__is_active=True) & Q(board__category__is_active=True)
		query_params = query_params & ~Q(board__in=unfollowed_boards)
		board_params = Q(board__user__in = followed_users) | Q(board__in=followed_boards) 

		qs = self.filter(query_params & board_params)

		qs = qs.select_related('board', 'domain', 'board__category', 'source_pin','board__user','created_user')
		
		if category:
			qs = qs.filter(board__category=category)
		return qs

	def active_pins(self):
		return self.filter(is_active=True, board__is_active=True,
			board__category__is_active=True, board__user__is_active=True).select_related('board', 'domain', 'board__category', 'source_pin','board__user','created_user')

	def get_number_of_pins_for_user(self, user):
		"""
		Returns number of active pins some user has created
		"""
		return self.active_pins().filter(board__user=user).count()

class LikeManager(models.Manager):

	def like_pin(self, pin, user):
		pin_ctype = ContentType.objects.get_for_model(pin)
		if self.filter(content_type__pk=pin_ctype.pk, object_id=pin.pk, user=user).count()==0:
			return self.create(content_object=pin, user=user)

	def get_number_of_likes_for_user(self, user):
		"""
		Returns number of likes for passed user's active pins
		"""
		from pins.models import Pin
		pin_ctype = ContentType.objects.get_for_model(Pin)
		pin_list = Pin.objects.active_pins().filter(board__user=user).values_list('pk', flat=True)
		return self.filter(content_type=pin_ctype, object_id__in=pin_list).count()

	class Meta:
		use_for_related_fields = True


class PinAdvertismentManager(models.Manager):

	def get_active_advertisment(self):
		now = datetime.datetime.now()
		date_q = (models.Q(active_from__lte=now) | models.Q(active_from=None)) & (models.Q(active_to__gte=now) | models.Q(active_to=None))
		impr_q = (models.Q(max_impressions__gt=models.F('current_impressions')) | models.Q(max_impressions=None))
		q = date_q & impr_q
		matches = list(self.filter(q, is_active=True))
		if len(matches)>0:
			m = random.choice(matches)
			self.filter(pk=m.pk).update(current_impressions= models.F('current_impressions')+1)
			return random.choice(matches)
		return None

