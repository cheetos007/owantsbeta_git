from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django import forms
from django.contrib.auth.models import User

class LoginFormTest(TestCase):

	def test_index_form_test(self):
		"""Test if there is login form in the index page"""
		response = self.client.get('/')
		self.assertIsInstance(response.context['login_form'], forms.Form)

	def test_index_form_render_test(self):
		response = self.client.get('/')
		self.assertIn('name="password"', response.content)

	def test_login_view(self):
		u = User.objects.create(email="user@example.org", username="Test user")
		u.set_password('password')
		u.save()

		form_data = {'email': u.email, 'password': 'password'}
		resp = self.client.post(reverse('acct_login'), form_data, follow=True)
		self.assertTrue(resp.context['user'].is_authenticated())


