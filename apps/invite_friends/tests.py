from urllib import urlencode

from django.test.client import RequestFactory
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.conf import settings
from django.utils import simplejson as json
from django.contrib.sessions.middleware import SessionMiddleware

from social_auth.models import UserSocialAuth

from invite_friends.models import EmailInvite, FacebookInvite
from invite_friends.forms import email_invite_form_factory
from invite_friends.helpers import get_invite_parameters, accept_invite, get_invite_from_request
from invite_friends.facebook import facebook_factory, FacebookAPIError


from pins.follow import follow

class BaseTestCase(TestCase):
	def setUp(self):
		u = User(username='username', email='email@example.org')
		u.set_password('password')
		u.save()
		self.user = u

class ModelTest(BaseTestCase):

	def test_code_generation(self):
		inv = EmailInvite.objects.create(user=self.user, email='test@example.org')
		self.assertTrue(len(inv.code), 32)

	def test_absolute_url(self):
		inv = EmailInvite.objects.create(user=self.user, email='test@example.org')
		self.assertEqual(inv.get_absolute_url(), 
				'%s?%s' % (reverse('acct_signup'), urlencode({'inv_type': 'EmailInvite', 'code': inv.code})))


class EmailInviteTest(BaseTestCase):

	def setUp(self):
		super(EmailInviteTest, self).setUp()
		self.old_installed_apps = settings.INSTALLED_APPS
		# remove django-mailer to properly test for outbound email
		if "mailer" in settings.INSTALLED_APPS:
			settings.INSTALLED_APPS.remove("mailer")
	
	def tearDown(self):
		settings.INSTALLED_APPS = self.old_installed_apps

	def test_form(self):
		form_class = email_invite_form_factory(self.user)

		data = {'email': 'test@example.org'}

		form = form_class(data)
		self.assertTrue(form.is_valid())
		inv = form.save()
		self.assertIsInstance(inv, EmailInvite)
		self.assertEqual(inv.user, self.user)
		self.assertEqual(inv.email, data['email'])

	def test_email_view(self):
		emails = [u'test1@example.org',u'test2@example.org']
		data = {
			'form-TOTAL_FORMS': u'3',
			'form-INITIAL_FORMS': u'0',
			'form-MAX_NUM_FORMS': u'',
			'form-0-email': emails[0],
			'form-1-email': emails[1],
			'personal_note': u'Some personal note',
			}
		resp = self.client.post(reverse('invite_friends_email'), data)
		#anonymous users don't have access to this view
		self.assertEqual(resp.status_code, 302)

		self.client.login(email=self.user.email, password='password')
		resp = self.client.get(reverse('invite_friends_email'))
		self.assertEqual(resp.status_code, 200)


		resp = self.client.post(reverse('invite_friends_email'), data, follow=True)
		self.assertEqual(resp.status_code, 200)
		
		created_invites = EmailInvite.objects.filter(user=self.user)
		
		self.assertEqual(created_invites.count(), 2)
		
		self.assertIn(created_invites[0].email, emails)

		self.assertEqual(created_invites[0].personal_note,data['personal_note'])

	def test_blank_emails(self):
		emails = [u'test1@example.org',u'test2@example.org']
		data = {
			'form-TOTAL_FORMS': u'3',
			'form-INITIAL_FORMS': u'0',
			'form-MAX_NUM_FORMS': u'',
			'form-0-email': '',
			'form-1-email': '',
			'personal_note': u'Some personal note',
			}

		self.client.login(email=self.user.email, password='password')

		resp = self.client.post(reverse('invite_friends_email'), data, follow=False)
		self.assertEqual(resp.status_code, 200)
		
		created_invites = EmailInvite.objects.filter(user=self.user)
		
		self.assertEqual(created_invites.count(), 0)

	def test_sent_email(self):
		EmailInvite.objects.create(user=self.user, email='test@example.org')
		self.assertEqual(len(mail.outbox), 1)

	def test_preview_view(self):
		self.client.login(email=self.user.email, password='password')
		resp = self.client.get(reverse('invite_friends_email_preview'))
		self.assertEqual(resp.status_code, 200)

	def test_preview_email_content(self):
		inv = EmailInvite.objects.create(user=self.user, email='test@example.org')
		self.client.login(email=self.user.email, password='password')
		resp = self.client.get(reverse('invite_friends_email_preview'), {'inv_pk': inv.pk })
		self.assertEqual(resp.content, mail.outbox[0].body)


class EmailInviteHelperTests(BaseTestCase):
	def setUp(self):
		super(EmailInviteHelperTests, self).setUp()
		self.factory = RequestFactory()
		self.middleware = SessionMiddleware()
		follow.flushdb()

	def _process_request(self, request):
		self.middleware.process_request(request)

	def test_request_parameter_processing(self):
		inv = EmailInvite.objects.create(user=self.user, email='test@example.org')
		req = self.factory.get(inv.get_absolute_url())
		self._process_request(req)
		url = get_invite_parameters(req)
		self.assertIn(inv.code, url)
		self.assertIn('EmailInvite', url)

	def test_get_invite_from_request(self):
		inv = EmailInvite.objects.create(user=self.user, email='test@example.org')
		req = self.factory.get(inv.get_absolute_url())
		self._process_request(req)
		self.assertEqual(get_invite_from_request(req), inv) 

	def test_invite_acceptance(self):
		inv = EmailInvite.objects.create(user=self.user, email='test@example.org')
		user = User.objects.create(username='test_user_123', email='test@example.org')
		req = self.factory.get(inv.get_absolute_url())
		accept_invite(req, user)
		inv = EmailInvite.objects.get(pk=inv.pk)
		self.assertEqual(inv.accepted_user, user)


		#assert that users follow each other by default
		self.assertEqual(follow.get_user_followers(self.user.pk),[user.pk])
		self.assertEqual(follow.get_user_followers(user.pk),[self.user.pk])





class AcceptEmailInviteTests(TestCase):
	def setUp(self):
		follow.flushdb()

	def test_accept_invite(self):
		u = User.objects.create(username='testuser', email='test@example.org')
		inv = EmailInvite.objects.create(user=u, email='test2@example.org')

		resp = self.client.get(inv.get_absolute_url())
		self.assertEqual(resp.status_code, 200)
		self.assertIn(inv.code, resp.content)

		resp = self.client.post(inv.get_absolute_url(), 
			{'username':'testuser2', 'password':'password', 
			'email': 'test2@example.org'}, follow=False)

		self.assertEqual(resp.status_code, 302)

		u2 = User.objects.get(username='testuser2')

		inv = EmailInvite.objects.get(pk=inv.pk)
		self.assertEqual(inv.accepted_user, u2)
		#assert that users follow each other by default
		self.assertEqual(follow.get_user_followers(u.pk),[u2.pk])
		self.assertEqual(follow.get_user_followers(u2.pk),[u.pk])


class FacebookBaseTest(TestCase):
	def setUp(self):
		self.fb = facebook_factory()

class TestFacebookInterface(FacebookBaseTest):

	def test_app_access_token(self):
		token = self.fb.get_app_access_token()
		self.assertEqual(len(token), 43)

	def test_create_test_user(self):
		user = self.fb.create_test_user()
		self.assertIn('id', user)
		self.assertIn('access_token', user)
		self.assertIn('email', user)

	def test_get_test_users(self):
		user = self.fb.create_test_user()
		test_users = self.fb.get_test_users()
		found = False
		for u in test_users:
			if u['id']==user['id']:
				found = True
		if not found:
			self.fail("Test user which is created is not in test user's list.")

	def test_get_user_info(self):
		user = self.fb.create_test_user()
		user_info = self.fb.get_user_info(user['id'])
		self.assertEqual(user['id'], user_info['id'])

	def test_delete_test_user(self):
		user = self.fb.create_test_user()
		self.fb.delete_test_user(user['id'])
		self.assertRaises(FacebookAPIError, self.fb.get_user_info, user['id'])

	def test_delete_test_users(self):
		user = self.fb.create_test_user()
		self.fb.delete_test_users()
		users = self.fb.get_test_users()
		self.assertEqual(len(users), 0)



class TestFacebookFriends(FacebookBaseTest):

	def tearDown(self):
		self.fb.delete_test_users()

	def test_get_user_friends(self):
		u = self.fb.create_test_user()
		friends = self.fb.get_user_friends(u)
		self.assertEqual(len(friends), 0)

	def test_friend_test_users(self):
		u = self.fb.create_test_user()
		u2 = self.fb.create_test_user()
		self.fb.friend_test_users(u, u2)

		friends = self.fb.get_user_friends(u)
		found = False
		for f in friends:
			if f['id']==u2['id']:
				found = True
		if not found:
			self.fail("%s not found in %s list of friends" % (u2['id'], u['id']))

		friends = self.fb.get_user_friends(u2)
		found = False
		for f in friends:
			if f['id']==u['id']:
				found = True
		if not found:
			self.fail("%s not found in %s list of friends" % (u['id'], u2['id']))

class TestFacebookViews(FacebookBaseTest):

	def setUp(self):
		super(TestFacebookViews, self).setUp()
		self.user = User.objects.create(username="testuser", email="test@example.org")
		self.user.set_password('password')
		self.user.save()
		self.unassociated_user = User.objects.create(username="testuser2", email="test@example.org")
		self.unassociated_user.set_password('password')
		self.unassociated_user.save()

		self.test_user = self.fb.create_test_user()
		self.association = UserSocialAuth.objects.create(user=self.user,provider='facebook', uid=self.test_user['id'], extra_data=json.dumps(self.test_user))
		self.test_user2 = self.fb.create_test_user(name="sometest")
		self.fb.friend_test_users(self.test_user, self.test_user2)

	def test_unassociated_view(self):
		self.client.login(username=self.unassociated_user.username, password='password')
		resp = self.client.get(reverse('invite_friends_facebook'))
		self.assertIn(reverse('socialauth_associate_begin', kwargs={'backend':'facebook'}), resp.content)

	def test_not_logged_in_view(self):
		resp = self.client.get(reverse('invite_friends_facebook'), follow=False)
		self.assertEqual(resp.status_code, 302)

	def test_associated_view(self):
		self.client.login(username=self.user.username, password='password')
		resp = self.client.get(reverse('invite_friends_facebook'))
		self.assertIn(self.test_user2['id'], resp.content)

	def test_send_invites(self):
		self.test_user3 = self.fb.create_test_user(name="moretest")
		fb_ids = ','.join([self.test_user2['id'], self.test_user3['id']])
		personal_note = 'Some personal note'

		self.client.login(username=self.user.username, password='password')
		resp = self.client.post(reverse('sent_facebook_invites'), {'fb_ids': fb_ids, 'note': personal_note})
		self.assertEqual(resp.status_code, 200)

		inv = FacebookInvite.objects.filter(user=self.user).values_list('facebook_user_id', flat=True)

		self.assertIn(self.test_user2['id'], inv)
		self.assertIn(self.test_user3['id'], inv)

		inv = FacebookInvite.objects.get(user=self.user, facebook_user_id=self.test_user2['id'])
		self.assertEqual(inv.personal_note, personal_note)



