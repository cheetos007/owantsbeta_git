import os
import datetime

from django.test import TestCase
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.exceptions import ValidationError

from pins.models import PinAdvertisment


class PinAdvertismentTest(TestCase):

	def test_pin_advertisment_validation(self):
		with self.assertRaises(ValidationError) as exc:
			PinAdvertisment.objects.create(image='/test/image.jpg').full_clean()
		with self.assertRaises(ValidationError) as exc:
			PinAdvertisment.objects.create(url='http://example.org').full_clean()
		with self.assertRaises(ValidationError) as exc:
			PinAdvertisment.objects.create().full_clean()


		
		#test if normal validation works fine (i.e. does not raise exceptions for valid cases)
		normal_ad = PinAdvertisment.objects.create(image='/test/image.jpg', url='http://example.org/', max_impressions=123)
		normal_ad.full_clean()
		PinAdvertisment.objects.create(html_code='<p>Test</p>', max_impressions=123).full_clean()

		with self.assertRaises(ValidationError) as exc:
			normal_ad.image=''
			normal_ad.save()
			normal_ad.full_clean()

	def test_advertisment_output(self):
		image_dir = os.path.join(os.path.dirname(settings.MEDIA_ROOT), 'default_images')
		image = os.path.join(image_dir, os.listdir(image_dir)[0])
		p = PinAdvertisment.objects.create(url='http://example.org/')
		p.image.save(os.path.basename(image),  ContentFile(open(image, 'rb').read()))

		output = p.get_advertisment()
		if not output.startswith('<a href'):
			self.fail("Pin advertisment image + link output failed.")

		p2 = PinAdvertisment.objects.create(html_code="<p>Test</p>")
		self.assertEqual(p2.get_advertisment(), "<p>Test</p>")

	def test_ad_selection(self):
		now = datetime.datetime.now()
		ad_start = now - datetime.timedelta(days=3)
		ad_end = now + datetime.timedelta(days=3)

		p1 = PinAdvertisment.objects.create(html_code="<p>Test</p>", active_from=ad_start, active_to=ad_end, 
			max_impressions=100, current_impressions=99)
		self.assertEqual(PinAdvertisment.objects.get_active_advertisment(), p1)

		p1.delete()
		p2 = PinAdvertisment.objects.create(html_code="<p>Test</p>", active_from=ad_start, active_to=ad_start,
		 max_impressions=100, current_impressions=99)
		self.assertEqual(PinAdvertisment.objects.get_active_advertisment(), None)

		p3 = PinAdvertisment.objects.create(html_code="<p>Test</p>", active_from = ad_start, active_to=ad_end, 
			max_impressions=100, current_impressions=100)

		self.assertEqual(PinAdvertisment.objects.get_active_advertisment(), None)

		p4 = PinAdvertisment.objects.create(html_code="<p>Test</p>", active_from = ad_start, 
			max_impressions=100, current_impressions=0)

		self.assertEqual(PinAdvertisment.objects.get_active_advertisment(), p4)

		#test if current impressions are incremented
		p4 = PinAdvertisment.objects.get(pk=p4.pk)

		PinAdvertisment.objects.all().delete()

		p5 = PinAdvertisment.objects.create(html_code="<p>test</p>", active_from=ad_end, active_to=ad_start)
		self.assertEqual(PinAdvertisment.objects.get_active_advertisment(), None)
		p5.delete()

		p6 = PinAdvertisment.objects.create(html_code="<p>test</p>", active_from=ad_start, active_to=ad_end)
		self.assertEqual(PinAdvertisment.objects.get_active_advertisment(), p6)

