from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth.models import User


class SignUpTest(TestCase):
    
    def setUp(self):
        self.old_installed_apps = settings.INSTALLED_APPS
        # remove django-mailer to properly test for outbound email
        if "mailer" in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.remove("mailer")
        
        self.EMAIL_AUTHENTICATION = getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION", False)
        User.objects.create_user("bob", "bob@example.com", "abc123")

    def tearDown(self):
        settings.INSTALLED_APPS = self.old_installed_apps

    def test_signup_response(self):
    	resp = self.client.get(reverse('acct_signup'))
    	self.assertEqual(resp.status_code, 200)

    def test_signup_user(self):
    	data = {'username': 'testuser', 'password':'password','email':'email@example.org'}
    	resp = self.client.post(reverse('acct_signup'), data, follow=True)
    	self.assertTrue(resp.context[0]['request'].user.is_authenticated())

    def test_signup_redirection(self):
    	data = {'username': 'testuser', 'password':'password','email':'email@example.org'}
    	resp = self.client.post(reverse('acct_signup'), data, follow=True)
    	self.assertGreater(len(resp.redirect_chain), 0)
    	self.assertIn(reverse('welcome_wizard'), resp.redirect_chain[0][0])
