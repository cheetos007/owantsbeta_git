import os

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from pins.models import Pin, Board, Category


image_dir = os.path.join(os.path.dirname(settings.MEDIA_ROOT), 'default_images')

class ButtonViewTests(TestCase):
	fixtures = ['test', 'initial']
	
	def setUp(self):
		self.user = User.objects.all()[0]
		self.user.set_password('password')
		self.user.save()
		self.category = Category.objects.create(name='Some category')
		self.board = Board.objects.create(name='Some board', category=self.category, user=self.user)


	def test_button_js_template(self):
		resp = self.client.get(reverse('button_js'))
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp['Content-Type'], 'application/javascript')

	def test_button_iframe_template_error(self):
		#assert that template contains error message if no params are passed
		resp = self.client.get(reverse('button_iframe'))
		self.assertEqual(resp.status_code, 200)
		self.assertIn('This field is required', resp.content)

	def test_button_iframe_template_success(self):
		#assert that template does not contain error message if params are passed
		data = {'url': 'http://example.org', 'image_url': 'http://example.org/image.png'}

		resp = self.client.get(reverse('button_iframe'), data)
		self.assertEqual(resp.status_code, 200)
		self.assertNotIn('This field is required', resp.content)

class ButtonModelTests(TestCase):
	fixtures = ['test', 'initial']
	def setUp(self):
		self.user = User.objects.all()[0]
		self.user.set_password('password')
		self.user.save()
		self.category = Category.objects.create(name='Some category')
		self.board = Board.objects.create(name='Some board', category=self.category, user=self.user)

	def test_pin_count(self):
		url = 'http://example.org/image.png'
		url2 = 'http://example.org/image2.png'
		p = Pin.objects.create(original_image_url=url, board=self.board)
		self.assertEqual(Pin.objects.get_pin_count_by_url(url), 1)
		self.assertEqual(Pin.objects.get_pin_count_by_url(url2), 0)

		p = Pin.objects.create(original_image_url=url2, board=self.board)
		p = Pin.objects.create(original_image_url=url2, board=self.board)
		self.assertEqual(Pin.objects.get_pin_count_by_url(url2), 2)



