import os
import json

from django.test import TestCase
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from pins.forms.pin_forms import get_pin_url_form
from pins.video_source_pool import parser_pool, BaseParser
from pins.video_sources import YoutubeVideoDescriptor, VimeoVideoDescriptor
from pins.models import Board, Category, Pin

class ParserPoolTests(TestCase):
	def test_registration(self):

		class TestParser(BaseParser):
			pass
		parser_pool.register_parser(TestParser)

		self.assertIsInstance(parser_pool.get_parser('TestParser'), TestParser)

	def test_autodiscovery(self):
		"""This test assumes that Youtube parser is automatically discovered"""
		self.assertTrue(issubclass(parser_pool.get_parser('YoutubeParser').__class__, BaseParser))
		self.assertIn(parser_pool.get_parser('YoutubeParser'), parser_pool.get_all_parsers())

	def test_unregister(self):
		"""As the previous test, this assumes that YouTube parser is automatically available"""
		self.assertTrue(issubclass(parser_pool.get_parser('TestParser').__class__, BaseParser))
		parser_pool.unregister_parser('TestParser')
		with self.assertRaises(KeyError):
			parser_pool.get_parser('TestParser')


class BaseVideoTest(TestCase):
	test_data_dir = os.path.join(os.path.dirname(__file__), 'video_test_data')

	def _get_test_file_contents(self, name):
		return open(os.path.join(self.test_data_dir, name),'rb').read()

class TestYouTubeParser(BaseVideoTest):


	def test_iframe(self):
		data = self._get_test_file_contents('youtube_iframe.html')
		
		results = parser_pool.get_parser_results('YoutubeParser', data)
		self.assertGreater(len(results), 0)
		self.assertEqual(results[0].video_id, 'Hn2bMpc2fkA')

	def test_a(self):
		data = self._get_test_file_contents('youtube_a.html')
		results = parser_pool.get_parser_results('YoutubeParser', data)
		self.assertGreater(len(results), 0)
		self.assertEqual(results[0].video_id, 'EfbhdZKPHro')

	def test_movie(self):
		data = self._get_test_file_contents('youtube_param.html')
		results = parser_pool.get_parser_results('YoutubeParser', data)
		self.assertGreater(len(results), 0)
		self.assertEqual(results[0].video_id, 'RSDUcKw-GOk')

	def test_direct_link(self):
		url = 'http://www.youtube.com/watch?v=oS6wfWu0JvA'
		results = parser_pool.get_parser_results('YoutubeParser', url)
		self.assertIsInstance(results[0], YoutubeVideoDescriptor)
		self.assertEqual(results[0].video_id, 'oS6wfWu0JvA')


class YoutubeDescriptorTest(BaseVideoTest):
	"""
	Tests if Youtube video descriptor returns correct data from video
	"""
	def test_descriptor_class(self):
		"""
		Tests if Youtube parser returns YoutubeVideoDescriptor instance 
		"""
		
		data = self._get_test_file_contents('youtube_iframe.html')
		results = parser_pool.get_parser_results('YoutubeParser', data)
		self.assertIsInstance(results[0], YoutubeVideoDescriptor)

	def test_descriptor_remote(self):
		data = self._get_test_file_contents('youtube_iframe.html')
		results = parser_pool.get_parser_results('YoutubeParser', data)
		self.assertTrue(results[0].get_remote_thumbnail().endswith('.jpg'))

	def test_descriptor_local_image(self):
		data = self._get_test_file_contents('youtube_iframe.html')
		results = parser_pool.get_parser_results('YoutubeParser', data)
		img = results[0].get_image_file()
		self.assertIsInstance(img, tuple)
		self.assertIsInstance(img[1], ContentFile)
		self.assertGreater(len(img[1]), 0)


class VimeoParserTest(BaseVideoTest):
	def test_iframe(self):
		data = self._get_test_file_contents('vimeo_iframe.html')
		
		results = parser_pool.get_parser_results('VimeoParser', data)
		self.assertGreater(len(results), 0)
		self.assertEqual(results[0].video_id, '38591304')

	def test_a(self):
		data = self._get_test_file_contents('vimeo_a.html')
		results = parser_pool.get_parser_results('VimeoParser', data)
		self.assertGreater(len(results), 0)
		self.assertEqual(results[0].video_id, '38591304')


	def test_direct_link(self):
		url = 'http://vimeo.com/40847329'
		results = parser_pool.get_parser_results('VimeoParser', url)
		self.assertIsInstance(results[0], VimeoVideoDescriptor)
		self.assertEqual(results[0].video_id, '40847329')

class VimeoDescriptorTest(BaseVideoTest):

	def test_descriptor_class(self):
		data = self._get_test_file_contents('vimeo_iframe.html')
		results = parser_pool.get_parser_results('VimeoParser', data)
		self.assertIsInstance(results[0], VimeoVideoDescriptor)

	def test_descriptor_remote(self):
		data = self._get_test_file_contents('vimeo_iframe.html')
		results = parser_pool.get_parser_results('VimeoParser', data)
		self.assertTrue(results[0].get_remote_thumbnail().endswith('.jpg'))

	def test_descriptor_local_image(self):
		data = self._get_test_file_contents('vimeo_iframe.html')
		results = parser_pool.get_parser_results('VimeoParser', data)
		img = results[0].get_image_file()
		self.assertIsInstance(img, tuple)
		self.assertIsInstance(img[1], ContentFile)
		self.assertGreater(len(img[1]), 0)


class TestDataCase(BaseVideoTest):
	fixtures = ['test', 'initial']
	
	def setUp(self):
		self.user = User.objects.all()[0]
		self.user.set_password('password')
		self.user.save()
		self.category = Category.objects.all()[0]
		self.board = Board.objects.create(user=self.user, category=self.category, name="Some board")
		self.client.login(email=self.user.email, password='password')



class VideoViewTests(TestDataCase):

	def test_video_view(self):
		url = 'http://wot.lv/content/alegria-cuba-libre'
		video_id = 'N2GYafXa_Cs'
		resp = self.client.post(reverse('website_media'), {'url':url})
		self.assertEqual(resp.status_code, 200)
		resp_json = json.loads(resp.content)
		self.assertIn('videos', resp_json)
		self.assertGreater(len(resp_json['videos']), 0)

	def test_video_submit(self):
		data = {'url': 'http://example.org', 'board':self.board.pk,'description':
			'Lorem ipsum', 'parser':'YoutubeParser', 'video_id': 'RSDUcKw-GOk'}
		resp = self.client.post(reverse('finish_web_pin'), data)
		self.assertEqual(resp.status_code, 302)

		#the following code verifies if pin is saved to database
		Pin.objects.get(video_id='RSDUcKw-GOk')

class VideoFormTests(TestDataCase):


	def test_form_submission(self):
		u = User.objects.all()[0]
		form_class = get_pin_url_form(u)

		data = {'url': 'http://example.org', 'board':self.board.pk,'description':
			'Lorem ipsum', 'parser':'YoutubeParser', 'video_id': 'RSDUcKw-GOk'}

		form = form_class(data)
		self.assertTrue(form.is_valid())
		pin = form.save()
		self.assertIsInstance(pin, Pin)
		self.assertGreater(pin.get_image().size, 0)
		


