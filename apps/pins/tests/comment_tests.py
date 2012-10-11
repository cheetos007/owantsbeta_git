from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment

from pins.models import Pin, Category, Board


class CommentTest(TestCase):
	fixtures = ['test', 'initial']
	
	def setUp(self):
		self.user = User.objects.all()[0]
		self.category = Category.objects.all()[0]
		self.board = Board.objects.create(name="some board 2", category = self.category, user=self.user)

	def test_pin_comment_annotation(self):
		p = Pin.objects.create(url="http://example.org", board=self.board)
		p2 = Pin.objects.create(url="http://example.com", board=self.board)
		pin_ctype = ContentType.objects.get_for_model(Pin)
		site = Site.objects.get_current()

		for pin in [p, p2]:
			for i in xrange(5):
				Comment.objects.create(content_type = pin_ctype, object_pk = pin.pk, user = self.user, comment="Comment %d" % i, site=site)
			for i in xrange(5):
				Comment.objects.create(content_type = pin_ctype, object_pk = pin.pk, user_name="Username", comment="Comment %d" % i, site=site)

		latest_pins = Pin.objects.latest_pins().annotate_with_comments(related_limit = 10)
		self.assertIsInstance(latest_pins[0].comments, list)
		self.assertEqual(len(latest_pins[0].comments), 10)
		self.assertEqual(latest_pins[0].comments[0].user_name, "Username")
		self.assertEqual(latest_pins[0].comments[-1].user, self.user)