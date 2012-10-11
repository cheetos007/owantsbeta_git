import time

from pins.seltests.base import BaseContentTestCase
from django.core.urlresolvers import reverse

from selenium.webdriver import ActionChains


class PinTestCase(BaseContentTestCase):

	def test_repin(self):
		self.login()
		#the button that needs to be clicked is hidden (shown on hover)
		#since actionchains didn't seem to be reliable, let's show the buttons via css
		self.inject_css("ul#pin-grid li .options-buttons { visibility:visible;}")

		self.find('span.option-repin').click()
		time.sleep(2)
		#fill in pin description
		self.driver.type_in('#repin-finish-content textarea#id_description', 'Some text')
		self.find('#repin-finish-content button').click()
		self.assertTrue(self.wait_for_text('.success', 'Pin repinned successfully'))

	def test_pin_it_error_reset(self):
		"""
		Refs #2122 Tests if popup error messages are resert when opening popup next time
		"""

		self.login()
		self.find('a#create-pin-popup').click()
		self.find('a#popup-add-pin-button').click()
		self.type_in('input#add-pin-website', 'http://example.org/')
		self.find('#add-pin-popup-content button').click()
		time.sleep(5)
		self.find('#add-pin-popup-finish-content span.close').click()
		time.sleep(1)
		self.find('a#create-pin-popup').click()
		self.find('a#popup-add-pin-button').click()
		self.type_in('input#add-pin-website', 'http://wot.lv/')
		self.find('#add-pin-popup-content button').click()
		
		#make sure error message is hidden now
		self.assertEqual(self.find('#pin-from-web-error').value_of_css_property('display'), 'none')

