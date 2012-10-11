import os
import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core import mail
from django.contrib.contenttypes.models import ContentType

image_dir = os.path.join(os.path.dirname(settings.MEDIA_ROOT), 'default_images')

class ProfileViewTests(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="test", email="test@example.org", password="password")
		self.user.first_name = "Test"
		self.user.last_name = "User"
		self.user.save()
		self.profile_edit_url = reverse('edit_profile')
		self.old_installed_apps = settings.INSTALLED_APPS
		# remove django-mailer to properly test for outbound email
		if "mailer" in settings.INSTALLED_APPS:
			settings.INSTALLED_APPS.remove("mailer")
	
	def tearDown(self):
		settings.INSTALLED_APPS = self.old_installed_apps

	def test_profile_url(self):
		self.assertEqual(self.user.get_absolute_url(), reverse('view_profile', kwargs={'username': self.user.username}))
	
	def test_profile_view(self):
		resp = self.client.get(self.user.get_absolute_url())
		self.assertEqual(resp.status_code, 200)

		self.assertIn(self.user.get_full_name(), resp.content)

	def test_profile_edit_view(self):
		resp = self.client.get(self.profile_edit_url, follow=False)
		self.assertEqual(resp.status_code, 302)

		self.client.login(username=self.user.username, password='password')
		resp = self.client.get(self.profile_edit_url)
		self.assertEqual(resp.status_code, 200)
		self.assertIn(_('Edit profile'), resp.content)

	def test_profile_edit_submit(self):
		self.client.login(username=self.user.username, password='password')
		data = {'username': 'test2', 'email': 'test2@example.org', 
			'location':'Sanfrancisko', 'about': 'Some about text', 
			'first_name': 'Test2', 'last_name': 'User2', 'website':'http://www.example.org/'}

		resp = self.client.post(self.profile_edit_url, data, follow=False)
		self.assertEqual(resp.status_code, 302)

		self.user = User.objects.get(pk=self.user.pk)

		#Confirmation e-mail about e-mail change
		self.assertEqual(len(mail.outbox), 1)
		user_fields = ['username', 'first_name','last_name']
		for f in user_fields:
			self.assertEqual(getattr(self.user, f), data[f])

		profile_fields = ['location', 'website','about']
		profile = self.user.get_profile()
		for f in profile_fields:
			self.assertEqual(getattr(profile, f), data[f])

	def test_duplicate_usernames(self):
		self.user2 = User.objects.create(username="test2", email="test2@example.org")

		self.client.login(username=self.user.username, password='password')
		data = {'username': 'test2', 'email': 'test@example.org'}

		resp = self.client.post(self.profile_edit_url, data, follow=False)
		self.assertEqual(resp.status_code, 200)
		self.assertIn(_('This username is already in use'), resp.content)

	def test_duplicate_email(self):
		self.user2 = User.objects.create(username="test2", email="test2@example.org")

		self.client.login(username=self.user.username, password='password')
		data = {'username': 'test', 'email': 'test2@example.org'}

		resp = self.client.post(self.profile_edit_url, data, follow=False)
		self.assertEqual(resp.status_code, 200)
		self.assertIn(_('This e-mail address is already in use'), resp.content)

	def test_no_email_change(self):
		self.client.login(username=self.user.username, password='password')
		data = {'username': 'test2', 'email': 'test@example.org'}

		resp = self.client.post(self.profile_edit_url, data, follow=False)
		self.assertEqual(resp.status_code, 302)
		self.assertEqual(len(mail.outbox), 0)

	def test_profile_image_upload(self):
		self.client.login(username=self.user.username, password='password')
		image = open(os.path.join(image_dir, os.listdir(image_dir)[0]),'rb')
		data = {'image': image}
		resp = self.client.post(reverse('upload_profile_image'), data)
		self.assertEqual(resp.status_code, 200)
		resp_json = json.loads(resp.content)

		#compare file size
		self.assertIn('media', resp_json['thumbnail'])
		image.seek(0)
		self.assertEqual(self.user.get_profile().image.size, len(image.read()))

	def test_delete_view(self):
		self.client.login(username=self.user.username, password='password')

		#check that user's password is asked for before deleting
		resp = self.client.get(reverse('delete_profile'))

		self.assertIn('password', resp.content)

		resp = self.client.post(reverse('delete_profile'), {'password': 'password'}, follow=False)

		self.assertEqual(resp.status_code, 302)

		self.assertRaises(User.DoesNotExist, User.objects.get, pk=self.user.pk)



class FollowViewTests(TestCase):
	fixtures = ['test', 'initial']
	
	def setUp(self):
		self.user = User.objects.all()[0]
		from pins.follow import follow
		self.follow = follow
		self.follow.flushdb()

	def test_following_view(self):
		self.client.login(email=self.user.email, password='password')
		user2 = User.objects.create(username='testuser')
		ctype = ContentType.objects.get_for_model(user2.__class__)
		follow_url = reverse('actstream_follow', kwargs={'content_type_id':ctype.pk, 'object_id': user2.pk})
		resp = self.client.get(follow_url)
		self.assertEqual(resp.status_code, 201)
		self.assertIn(self.user.pk, self.follow.get_user_followers(user2.pk))
		self.assertIn(user2.pk, self.follow.get_user_following(self.user.pk))

	def test_following_list(self):
		self.client.login(email=self.user.email, password='password')
		user2 = User.objects.create(username='testuser')
		ctype = ContentType.objects.get_for_model(user2.__class__)
		follow_url = reverse('actstream_follow', kwargs={'content_type_id':ctype.pk, 'object_id': user2.pk})
		self.client.get(follow_url)

		resp = self.client.get(reverse('following_users'))

		self.assertIn(user2.username, resp.content)






