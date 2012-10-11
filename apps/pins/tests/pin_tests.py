import os
import datetime
import random
import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from pins.models import Board, Pin, Category, Like
from pins.forms import get_repin_form, get_pin_url_form

image_dir = os.path.join(os.path.dirname(settings.MEDIA_ROOT), 'default_images')


class BoardTests(TestCase):
	fixtures = ['test', 'initial']


	def setUp(self):
		self.user = User.objects.all()[0]
		self.category = Category.objects.all()[0]

	def test_create_board(self):
		b = Board.objects.create(user=self.user, category=self.category, name="Some board")
		public_boards = Board.objects.get_user_public_boards(self.user)
		
		self.assertIn(b, public_boards)

	def test_inactive_board(self):
		b = Board.objects.create(user=self.user, category=self.category, name="Some board",
			 is_active=False)
		public_boards = Board.objects.get_user_public_boards(self.user)
		
		self.assertNotIn(b, public_boards)

	def test_inactive_category(self):
		inactive_cat = Category.objects.create(name="Some name", is_active=False)
		b = Board.objects.create(user=self.user, category=inactive_cat, name="Some board")
		public_boards = Board.objects.get_user_public_boards(self.user)
		
		self.assertNotIn(b, public_boards)

	def test_annotate_with_pins(self):
		b = Board.objects.create(user=self.user, category=self.category, name="some board")
		b2 = Board.objects.create(user=self.user, category=self.category, name="Other board")
		images = [os.path.join(image_dir, f) for f in os.listdir(image_dir)]
		p1 = Pin.objects.create(board=b)
		img = random.choice(images)
		p1.image.save(os.path.basename(img),  ContentFile(open(img, 'rb').read()))

		p2 = Pin.objects.create(board=b2, is_repin=True, source_pin=p1)

		boards = Board.objects.filter(pk=b2.pk).annotate_with_pins()
		self.assertIsInstance(boards[0].pins[0].get_image(), models.FileField.attr_class)


class PinTests(TestCase):
	fixtures = ['test', 'initial']
	
	def setUp(self):
		self.user = User.objects.all()[0]
		self.category = Category.objects.create(name='Some category')
		self.board = Board.objects.create(name='Some board', category=self.category, user=self.user)


	def test_latest_pins(self):
		p = Pin.objects.create(url="http://example.org/", board=self.board)
		latest = Pin.objects.latest_pins()
		self.assertIn(p, latest)

		#tests if pin on inactive board is not displayed
		b = Board.objects.create(is_active=False, user=self.user, category=self.category)
		p = Pin.objects.create(url="http://example.org/", board=b)
		latest = Pin.objects.latest_pins()
		self.assertNotIn(p, latest)

		#tests if pin on inactive category is not displayed
		c = Category.objects.create(name="Some category", is_active=False)
		b = Board.objects.create(is_active=True, user=self.user, category=c)
		p = Pin.objects.create(url="http://example.org/", board=b)
		latest = Pin.objects.latest_pins()
		self.assertNotIn(p, latest)

	def test_pin_domain(self):
		p = Pin.objects.create(url="http://example.org/", board=self.board)
		self.assertEquals(str(p.domain), "example.org")

	def test_likes(self):
		p = Pin.objects.create(url="http://example.org/", board=self.board)
		self.assertEqual(p.number_of_likes, 0)
		Like.objects.like_pin(p, self.user)

		p = Pin.objects.get(pk = p.pk)
		self.assertEqual(p.number_of_likes, 1)

		Like.objects.like_pin(p, self.user)
		p = Pin.objects.get(pk = p.pk)
		self.assertEqual(p.number_of_likes, 1)

		Like.objects.all().delete()
		p = Pin.objects.get(pk = p.pk)
		self.assertEqual(p.number_of_likes, 0)

	def test_pin_from_url(self):
		form_class = get_pin_url_form(self.user)
		data = {'board': self.board.pk, 'description': 'Some test description', 
		'url':'http://wot.lv/', 
		'image_url': 'https://lh5.googleusercontent.com/-uqDGD8tYhOg/Tx8FK52WrsI/AAAAAAAABP8/gylZJOCX6V4/w859-h572-k/Picture%2B001.jpg'}
		form = form_class(data)
		self.assertTrue(form.is_valid())
		pin = form.save()
		self.assertIsInstance(pin.get_image(), models.FileField.attr_class)
		self.assertEqual(pin.url, 'http://wot.lv/')
		self.assertEqual(pin.board, self.board)


class PinViewsTests(TestCase):
	fixtures = ['test', 'initial']
	
	def setUp(self):
		self.user = User.objects.all()[0]
		self.user.set_password('password')
		self.user.save()
		self.category = Category.objects.create(name='Some category')
		self.board = Board.objects.create(name='Some board', category=self.category, user=self.user)
		self.image = open(os.path.join(image_dir, os.listdir(image_dir)[0]),'rb')

	def test_pin_upload(self):
		
		self.client.login(email=self.user.email, password='password')
		data = {'image': self.image}
		resp = self.client.post(reverse('upload_pin'), data)
		self.assertEqual(resp.status_code, 200)
		resp_json = json.loads(resp.content)
		self.assertIn('pin_pk', resp_json)
		self.assertIn('thumbnail', resp_json)

	def test_website_media(self):
		url = 'http://wot.lv/content/russian-army-surplus'
		self.client.login(email=self.user.email, password='password')

		data = {'url': url}
		resp = self.client.post(reverse('website_media'), data)
		self.assertEqual(resp.status_code, 200)
		resp_json = json.loads(resp.content)
		self.assertIn('images', resp_json)
		self.assertTrue(len(resp_json['images'])>0)

	def test_website_media_spoki(self):
		url = 'spoki.lv'
		self.client.login(email=self.user.email, password='password')

		data = {'url': url}
		resp = self.client.post(reverse('website_media'), data)
		self.assertEqual(resp.status_code, 200)
		resp_json = json.loads(resp.content)
		if 'message' in resp_json and 'timed out' in resp_json['message']:
			#spoki.lv sometimes times out.
			return
		self.assertIn('images', resp_json)
		self.assertTrue(len(resp_json['images'])>0)

	def test_website_media_failure(self):
		url = 'nonexistantbutvalidurl.org'
		self.client.login(email=self.user.email, password='password')

		data = {'url': url}
		resp = self.client.post(reverse('website_media'), data)
		self.assertEqual(resp.status_code, 200)
		resp_json = json.loads(resp.content)
		self.assertIn('status', resp_json)
		self.assertEqual(resp_json['status'], 'nok')

	def test_finish_long_url(self):
		"""
		Very long URL's are truncated by MySQL when saved as image.
		"""

		url = 'http://faili.wot.lv/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.jpg'
		self.client.login(email=self.user.email, password='password')
		data = {'image_url': url, 'board': self.board.pk, 'description': 
			'Lorem', 'url': 'http://wot.lv/'}

		resp = self.client.post(reverse('finish_web_pin'), data, follow=True)

		self.assertIn('Pin created successfully', resp.content)

		#this should be the pin we have added, if tests are not somehow run in parallel
		latest_pin = Pin.objects.order_by('-id')[0]

		self.assertGreater(latest_pin.get_image().size, 0)


	def test_pin_popup(self):
		p = Pin.objects.create(url="http://example.org/", board=self.board, description="Some text")
		resp = self.client.get(p.get_popup_url())
		self.assertEqual(resp.status_code, 200)
		self.assertIn("Some text", resp.content)

	def test_pin_popup_manage_links(self):
		"""
		Refs #2123 - tests if pin popup contains edit/delete links (for pin author only)
		"""
		p = Pin.objects.create(url="http://example.org/", board=self.board, description="Some text")
		resp = self.client.get(p.get_popup_url())
		self.assertEqual(resp.status_code, 200)
		self.assertNotIn("Edit", resp.content)
		self.assertNotIn("Delete", resp.content)

		self.client.login(email=self.user.email, password='password')
		resp = self.client.get(p.get_popup_url())
		self.assertEqual(resp.status_code, 200)
		self.assertIn("Edit", resp.content)
		self.assertIn("Delete", resp.content)

	def test_pin_popup_user_profile_link(self):
		"""Refs #2128 - add link to user's account for pin popup"""
		
		p = Pin.objects.create(url="http://example.org/", board=self.board, description="Some text")
		resp = self.client.get(p.get_popup_url())
		self.assertEqual(resp.status_code, 200)
		self.assertIn(self.board.user.get_absolute_url(), resp.content)

	def test_repin_information(self):
		source_pin = Pin.objects.create(url="http://example.org/", board=self.board)

		self.client.login(email=self.user.email, password='password')
		imagefile = ContentFile(self.image.read())
		source_pin.image.save("image.png", imagefile)

		repin = Pin.objects.create(is_repin=True, source_pin=source_pin, board=self.board)

		resp = self.client.get(reverse('pin_information'), {'pin_pk': repin.pk})
		resp_json = json.loads(resp.content)
		self.assertEqual(resp_json['status'], 'ok')
		self.assertIn('thumbnail', resp_json)






class TestRepin(TestCase):
	fixtures = ['test','initial']

	def setUp(self):
		self.user = User.objects.all()[0]
		self.category = Category.objects.create(name='Some category')
		self.board = Board.objects.create(name='Some board', category=self.category, user=self.user)
		self.image = open(settings.MEDIA_ROOT + '/default_avatar.png', "r")

	def test_repin(self):
		source_pin = Pin.objects.create(url="http://example.org/", board=self.board)
		imagefile = ContentFile(self.image.read())
		source_pin.image.save("image.png", imagefile)

		repin = Pin.objects.create(is_repin=True, source_pin=source_pin)

		self.assertEqual(source_pin.image, repin.get_image())

		source_pin = Pin.objects.get(pk=source_pin.pk)
		self.assertEqual(source_pin.number_of_repins, 1)

	def test_repin_form(self):
		source_pin = Pin.objects.create(url="http://example.org/", board=self.board)
		imagefile = ContentFile(self.image.read())
		source_pin.image.save("image.png", imagefile)

		data = {'repinned_pin': source_pin.pk, 'board': self.board.pk, 
			'description': "Some description"}
		form = get_repin_form(self.user)(data)
		self.assertTrue(form.is_valid())
		pin = form.save()
		self.assertTrue(pin.is_repin)

		self.assertEqual(pin.get_image(), source_pin.image)

		source_pin = Pin.objects.get(pk=source_pin.pk)
		
		self.assertEqual(source_pin.number_of_repins, 1)
		
		self.assertEqual(pin.number_of_repins, 0)

	def test_repin_like(self):
		source_pin = Pin.objects.create(url="http://example.org/", board=self.board)
		imagefile = ContentFile(self.image.read())
		source_pin.image.save("image.png", imagefile)
		repin = Pin.objects.create(is_repin=True, source_pin=source_pin)

		
		self.assertEqual(source_pin.number_of_likes, 0)
		Like.objects.like_pin(repin, self.user)

		source_pin = Pin.objects.get(pk=source_pin.pk)
		self.assertEqual(source_pin.number_of_likes, 1)

		repin = Pin.objects.get(pk=repin.pk)
		self.assertEqual(source_pin.number_of_likes, 1)

	def test_double_repin(self):
		source_pin = Pin.objects.create(url="http://example.org/", board=self.board)
		imagefile = ContentFile(self.image.read())
		source_pin.image.save("image.png", imagefile)

		data = {'repinned_pin': source_pin.pk, 
			'board': self.board.pk, 'description': "Some description"}
		form = get_repin_form(self.user)(data)
		form.is_valid()
		repin = form.save()
		self.assertTrue(repin.is_repin)

		data = {'repinned_pin': repin.pk, 'board': self.board.pk, 
			'description': "Some description"}
		form = get_repin_form(self.user)(data)
		form.is_valid()
		repin2 = form.save()

		self.assertEqual(repin2.source_pin, source_pin)
		self.assertEqual(repin2.repinned_pin, repin)


