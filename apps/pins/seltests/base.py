from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.base import ContentFile


from django_selenium.testcases import SeleniumTestCase

from pins.models import Pin, Board, Category


class BaseContentTestCase(SeleniumTestCase):

	fixtures = ['test', 'initial']

	def setUp(self):
		super(BaseContentTestCase, self).setUp()
		self.user = User.objects.all()[0]
		self.user.set_password('password')
		self.user.save()
		self.category = Category.objects.create(name='Some category')
		self.board = Board.objects.create(name='Some board', category=self.category, user=self.user)
		self.pin = Pin.objects.create(url="http://example.org/", board=self.board)

		imagefile = ContentFile(open(settings.MEDIA_ROOT + '/category_images/architecture.jpg', "r").read())
		self.pin.image.save("image.jpg", imagefile)
		self.pin.save()

	def login(self):
		self.driver.open_url(reverse("acct_login"))
		self.driver.type_in("#id_email", self.user.email)
		self.driver.type_in("#id_password", "password")
		self.driver.click("button.submit-login-button")
		assert self.driver.is_text_present("Successfully logged in")

	def inject_css(self, css_style):
		"""Injects CSS style rules in current page via JS"""
		css_snippet = "<style type=\"text/css\">%s</style>" % css_style
		js_snippet = "$('%s').appendTo('html > head');" % css_snippet

		self.driver.driver.execute_script(js_snippet)


