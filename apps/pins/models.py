from urlparse import urlparse
import datetime

from django.utils.safestring import mark_safe
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib import comments
from django.contrib.comments.signals import comment_was_posted
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models import Count
from django.utils.translation import trans_real
from django.core.cache import cache
from django.core.exceptions import ValidationError
from sorl.thumbnail import get_thumbnail

from modeltranslation.translator import translator, TranslationOptions
from sorl.thumbnail import ImageField
from actstream import action

from audit_fields.models import BaseAuditModel

from pins.helpers import get_domain_name, get_affiliate_func
from pins.managers import BoardManager, CategoryManager, PinManager, LikeManager, PinAdvertismentManager
import pins.signals
from pins import CATEGORY_LIST_CACHE_KEY, USER_BOARDS_CACHE_KEY, CACHE_TIMEOUT
from pins.video_source_pool import parser_pool
from pins.follow import follow


affiliate_processor_func = get_affiliate_func()

class Category(BaseAuditModel):
    """
     Site-wide category model for boards
     """
    name = models.CharField(verbose_name=_("name"), max_length=255)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    image = ImageField(verbose_name=_('image'), upload_to="category_images/", blank=True)
    show_upon_signup = models.BooleanField(verbose_name=_('show upon signup'), default=True,
        help_text=_('Whether to show this category when user first signs up?'))
    recommended_users_to_follow = models.ManyToManyField(User, blank=True, verbose_name=_('recommended users to follow'),
        help_text=_('Users from this list will be preferred when choosing which users will be recommended to follow after signup.'))


    objects = CategoryManager()

    class Meta:
        verbose_name = _("pin category")
        verbose_name_plural = _("pin categories")

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("single_category", [self.pk, slugify(self.name)])


    def suggest_users_to_follow(self, users_needed=3, number_of_pins_preferred=40):
        """This method returns a list of users to follow for this category.
          Users to follow are selected primarily from:
          1) Category model's recommended_users_to_follow field
          2) At random from users with at least number_of_pins_preferred pins
          3) At random from all users with pins in selected categories
          """
        users_to_follow = []
        if self.recommended_users_to_follow.count()>=users_needed:
            users_to_follow = list(self.recommended_users_to_follow.order_by('?')[:users_needed-1])
        else:
            users_to_follow.extend(list(self.recommended_users_to_follow.all()))
            base_user_qs = User.objects.filter(pins_pin_created_set__board__category=self, is_active=True).exclude(pk__in=[u.pk for u in users_to_follow])

            preferred_qs = base_user_qs.annotate(number_of_pins=Count('pins_pin_created_set__pk')).\
            filter(number_of_pins__gte=number_of_pins_preferred)

            users_needed = users_needed - len(users_to_follow)

            if preferred_qs.count()>=users_needed:
                users_to_follow.extend(list(preferred_qs.order_by('?')[:users_needed-1]))
            else:
                users_to_follow.extend(list(preferred_qs.all()))

                users_needed = users_needed - len(users_to_follow)
                if users_needed>0:
                    base_user_qs.exclude(pk__in=[u.pk for u in users_to_follow])
                    if base_user_qs.count()>=users_needed:
                        users_to_follow.extend(list(base_user_qs.order_by('?')[:users_needed-1]))
                    else:
                        users_to_follow.extend(list(base_user_qs.all()))

        return users_to_follow




def update_category_cache(sender, instance, **kwargs):
    for l in settings.LANGUAGES:
        l = l[0]
        trans_real.activate(l)
        cache.set('%s_%s' % (CATEGORY_LIST_CACHE_KEY, l ), Category.objects.filter(is_active=True), CACHE_TIMEOUT)
        trans_real.deactivate()


models.signals.post_save.connect(update_category_cache, sender=Category)
models.signals.post_delete.connect(update_category_cache, sender=Category)

class DefaultBoard(BaseAuditModel):
    """
     This model represents default boards, which are presented to user right after signup.
     User can then select which of these boards to have in their new account.
     """
    name = models.CharField(verbose_name=_("name"), max_length=255)
    category = models.ForeignKey(Category, verbose_name=_('category'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _("default board")
        verbose_name_plural = _("default boards")

    def __unicode__(self):
        return self.name

class Board(BaseAuditModel):
    """
     Board is a collection of images from single user. Board may have category.
     """
    name = models.CharField(verbose_name=_("name"), max_length=255)
    category = models.ForeignKey(Category, verbose_name=_("category"), blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=_('user'), related_name="board_set")
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    objects = BoardManager()

    class Meta:
        verbose_name = _("board")
        verbose_name_plural = _("boards")

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("single_board", [self.pk, slugify(self.name)])

def update_boards_cache(sender, instance, **kwargs):
    boards = Board.objects.filter(is_active=True, user=instance.user_id, category__is_active=True).select_related()
    cache.set('%s_%d' % (USER_BOARDS_CACHE_KEY, instance.user_id), boards, CACHE_TIMEOUT)

models.signals.post_save.connect(update_boards_cache, sender=Board)
models.signals.post_delete.connect(update_boards_cache, sender=Board)


class Pin(BaseAuditModel):
    """
     Model for single pin/image.
     Image can only be None in case is_repin is True and both source_pin and repinned_pin are full.
     In case image is None, source_pin.image should be used instead.
     """
    url = models.URLField(max_length=255, verbose_name=_("url"), verify_exists=False, blank=True)
    image = ImageField(verbose_name=_("image"), upload_to="pins/%y/%m/%d", blank=True)
    owant_type = models.CharField(verbose_name=_('owant type'), max_length=4, default='want',choices=(('own', _('Own')), ('want', _('Want'))))
    original_image_url = models.URLField(max_length=255, verbose_name=_('original image url'), verify_exists=True, blank=True)

    video_id = models.CharField(verbose_name=_('video id'), max_length=255, blank=True)
    video_parser = models.CharField(verbose_name=_('video parser'), max_length=255, blank=True)

    is_repin = models.BooleanField(verbose_name=_("is repin"), default=False)
    source_pin = models.ForeignKey("self", verbose_name=_("source pin"), blank=True,
        null=True, related_name='all_repinned_set')

    repinned_pin = models.ForeignKey("self", verbose_name=_("repinned pin"), blank=True, null=True,
        related_name='first_level_repinned_set')
    board = models.ForeignKey(Board, verbose_name=_('board'), blank=True, null=True)
    is_flagged = models.BooleanField(verbose_name=_('is flagged'), default=False)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    description = models.TextField(verbose_name=_('description'), blank=True)

    domain = models.ForeignKey('PinDomain', verbose_name=_('domain'), blank=True, null=True)

    pin_source = models.CharField(verbose_name=_('pin method'), choices=(('upload', _('Uploaded file')), ('url', _('Added from URL')),
                                                                         ('bookmarklet', _('Added via bookmarklet'))), default='url', max_length=20,
        help_text=_('How was this pin added to the site.'))

    #denormalized_fields for blazingly fast selects
    #these fields are updated in signal handlers
    number_of_repins = models.IntegerField(verbose_name=_('number of repins'), default=0)
    number_of_likes = models.IntegerField(verbose_name=_('number of likes'), default=0)
    number_of_comments = models.IntegerField(verbose_name=_('number of comments'), default=0)


    objects = PinManager()


    class Meta:
        verbose_name = _("pin")
        verbose_name_plural = _("pins")
        ordering = ['-id']

    def __unicode__(self):
        return self.description

    @models.permalink
    def get_absolute_url(self):
        return ('single_pin', (self.pk,))

    @models.permalink
    def get_popup_url(self):
        return ('single_pin_popup', (self.pk,))

    def save(self, *args, **kwargs):
        if not self.domain_id and self.url:
            domain = get_domain_name(self.url)
            self.domain = PinDomain.objects.get_or_create(domain_name=domain)[0]

        super(Pin, self).save(*args, **kwargs)

    def get_image(self):
        if self.is_repin:
            return self.source_pin.image
        else:
            return self.image

    def get_number_of_repins(self):
        """
          Returns number of repins for display in templates.
          If this is a re-pin, return number of repins for original pin, otherwise return number of repins for this pin
          """
        if self.source_pin:
            return self.source_pin.number_of_repins
        else:
            return self.number_of_repins

    def get_number_of_likes(self):
        """
          Returns number of likes for display in templates.
          If this is a re-pin, return number of likes for original pin, otherwise return number of likes for this pin
          """
        if self.source_pin:
            return self.source_pin.number_of_likes
        else:
            return self.number_of_likes

    def get_target_url(self, request):

        if affiliate_processor_func:
            return affiliate_processor_func(self, request)
        else:
            return self.url

    def get_video_markup(self):
        assert self.video_id and self.video_parser

        desc = parser_pool.get_video_descriptor(self.video_parser, self.video_id)

        return desc.get_video_markup(626, 400)



class PinDomain(BaseAuditModel):
    """
     Stores domain name for pin- used mainly to track pins from single domain name
     and show them together
     """

    domain_name = models.CharField(verbose_name=_('domain name'), max_length=255, unique=True)

    def __unicode__(self):
        return self.domain_name

class Like(BaseAuditModel):
    """
     A mere existance of instance of this model means that someone has "liked" the related object (Pin, Board, etc)
     """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User)

    objects = LikeManager()

@receiver(models.signals.post_save, sender=Like, dispatch_uid="pins.models")
def update_likes(sender, instance, created, raw, **kwargs):
    if not raw and created:
        pin = instance.content_object.source_pin or instance.content_object
        pin.number_of_likes += 1
        pin.save()
        action.send(instance.user, verb='liked', action_object=instance.content_object)

@receiver(models.signals.post_delete, sender=Like, dispatch_uid="pins.models")
def remove_likes(sender, instance, **kwargs):
    if instance.content_object:
        pin = instance.content_object.source_pin or instance.content_object
        if pin:
            pin.number_of_likes -= 1
            pin.save()


@receiver(models.signals.pre_save, sender=Pin, dispatch_uid="pins.models")
def update_repins(sender, instance, raw, **kwargs):
    if not raw and instance.is_repin:
        if not instance.pk and instance.is_active:
            #first save
            instance.source_pin.number_of_repins += 1
            instance.source_pin.save()
        else:
            previous_inst = Pin.objects.get(pk=instance.pk)
            if previous_inst.is_active == False and instance.is_active == True:
                #instance is "created"
                instance.source_pin.number_of_repins += 1
                instance.source_pin.save()
            elif previous_inst.is_active == True and instance.is_active == False:
                #instance is "deleted"
                instance.source_pin.number_of_repins -= 1
                instance.source_pin.save()


@receiver(pins.signals.pin_finished, dispatch_uid="pins.models")
def create_actions(sender, instance, **kwargs):
    if instance.is_repin:
        action.send(instance.created_user, verb='repinned', action_object=instance, target=instance.board)
    else:
        action.send(instance.created_user, verb='pinned', action_object=instance, target=instance.board)


@receiver(comment_was_posted, sender=comments.models.Comment, dispatch_uid="pins.models")
def update_comment_count(sender, comment, request, **kwargs):
    """Increment number of comments when comment is posted. Currently only handles pins."""
    Pin.objects.filter(pk=comment.object_pk).update(number_of_comments = models.F('number_of_comments')+1)
    action.send(request.user, verb='commented', action_object=comment.content_object)

@receiver(action, dispatch_uid="pins.models")
def update_follow_redis(sender, verb, **kwargs):
    actor = sender
    target = kwargs.pop('target', False)

    if target and isinstance(target, User):
        if verb ==_('started following'):
            follow.add_user_follower(target.pk, actor.pk)
        elif verb == _('stopped following'):
            follow.delete_user_follower(target.pk, actor.pk)
    elif isinstance(target, Board):
        if verb ==_('started following'):
            follow.remove_user_unfollowed_board(actor.pk, target.pk)
            follow.add_user_followed_board(actor.pk, target.pk)
        elif verb == _('stopped following'):
            follow.remove_user_followed_board(actor.pk, target.pk)
            follow.add_user_unfollowed_board(actor.pk, target.pk)




class PinAdvertisment(BaseAuditModel):
    """
     This model represents single advertisment which is added to each page of pins shown
     (in all views where pins are displayed: index, boards, category views etc.).
     Either linkable image or HTML snippet is shown. If both image + url fields and HTML snippet is filled in,
     image + url takes precendence.
     Advertisments to show are chosen the following way:
     advertisments which are active and active_from<current date and active_to>current_date and current_impressions<max_impressions (if max_impressions is defined)
     are shown. If more than one advertisment matches these filters, advertisment is selected randomly from matching ads.
     """

    image = ImageField(verbose_name=_('image'), upload_to="pin_advertisments/%y/%m/%d/", blank=True)
    url = models.URLField(max_length=255, verbose_name=_("url"), verify_exists=False, blank=True)
    html_code = models.TextField(verbose_name=_('HTML code'), blank=True, help_text=_('This field is only required if you don\'t fill image and url fields.'))
    active_from = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('active_from'))
    active_to = models.DateTimeField(verbose_name=_('active to'),
        help_text=_('At what datetime the ad won\'t be displayed anymore.'), null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    max_impressions = models.PositiveIntegerField(verbose_name=_('maximum impressions'), blank=True, null=True)
    current_impressions = models.PositiveIntegerField(verbose_name=_('current impressions'), default=0)
    objects = PinAdvertismentManager()

    #this attribute is used to tell pins and advertisments apart
    is_advertisment = True


    class Meta:
        verbose_name = _('pin advertisment')
        verbose_name_plural = _('pin advertisments')


    def clean(self):
        if self.image == '' and self.url== '' and self.html_code=='':
            raise ValidationError(_("Either image and url fields or HTML code field needs to be filled in."))
        if self.image == '' and self.url != '' and self.html_code=='':
            raise ValidationError(_("Image field needs to be filled in."))
        if self.image != '' and self.url=='' and self.html_code=='':
            raise ValidationError(_("Url field needs to be filled in."))

    def get_advertisment(self):
        retval = ''
        if self.image and self.url:
            image = get_thumbnail(self.image, '210', crop='center')
            retval = '<a href="%s"><img src="%s" height="%d" width="%d" alt=""/></a>' % (self.url, image.url, image.height, image.width)
        else:
            retval = self.html_code

        return mark_safe(retval)

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Category, CategoryTranslationOptions)

class DefaultBoardTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(DefaultBoard, DefaultBoardTranslationOptions)