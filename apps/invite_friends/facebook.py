import urllib3
from urllib3.exceptions import HTTPError

from django.core.files.base import ContentFile
from django.core.cache import cache
from django.utils import simplejson as json
from django.conf import settings

from site_settings.helpers import get_setting


class FacebookAPIError(Exception):
	pass


def facebook_factory():
	"""Returns Facebook API object with either settings.TEST_* API parameters, or API parameters from site_settings"""
	if settings.INSIDE_TESTING:
		params = {'app_id': settings.TEST_FACEBOOK_APP_ID,'app_secret': settings.TEST_FACEBOOK_API_SECRET}
	else:
		params = {'app_id': get_setting('facebook_app_id'), 'app_secret': get_setting('facebook_api_secret')}
	return Facebook(**params)

class Facebook(object):
	def __init__(self, app_id, app_secret):
		self.app_id = app_id
		self.app_secret = app_secret
		self._app_access_token = None

		self.pool = urllib3.PoolManager()

	def _bool_to_str(self, val):
		if val:
			return 'true'
		return 'false'

	def get_app_access_token(self):
		cache_key = 'app_token:%s' % self.app_secret
		self._app_access_token = cache.get(cache_key)
		if not self._app_access_token:
			
			resp = self.pool.request('GET', 'https://graph.facebook.com/oauth/access_token', 
					{'client_id': self.app_id, 'client_secret': self.app_secret, 
					'grant_type': 'client_credentials'})
			if resp.status == 200:
				token = resp.data.split('=')[1]
				self._app_access_token = token
				cache.set(cache_key, token, 24*3600)
			else:
				raise FacebookAPIError("API application id or client secret is incorrect!")
		return self._app_access_token

	def create_test_user(self, name=None, installed=True, locale="en_US", permissions="read_stream"):
		app_token = self.get_app_access_token()
		data = {'name': name, 'installed': self._bool_to_str(installed),
			'locale': locale, 'permissions': permissions, 'access_token': app_token,
			'method': 'post'}
		if not name:
			data.pop('name')

		url = 'https://graph.facebook.com/%s/accounts/test-users' % self.app_id
		resp = self.pool.request('GET', url, data)
		if resp.status == 200:
			user = json.loads(resp.data)
			return user
		else:
			raise FacebookAPIError("Could not complete API request: " + resp.data)

	def get_test_users(self):
		url = 'https://graph.facebook.com/%s/accounts/test-users' % self.app_id
		data = {'access_token': self.get_app_access_token()}
		resp = self.pool.request('GET', url, data)
		if resp.status == 200:
			return json.loads(resp.data)['data']
		else:
			raise FacebookAPIError("Could not complete API request: " + resp.data)

	def get_user_info(self, user_id):
		url = 'https://graph.facebook.com/%s' % str(user_id)
		resp = self.pool.request('GET', url)
		if resp.status==200:
			data = json.loads(resp.data)
			if not data:
				raise FacebookAPIError("User with id of %s not found" % str(user_id))
			return data
		else:
			raise FacebookAPIError("Could not complete API request: " + resp.data)

	def delete_test_user(self, user_id):
		url = 'https://graph.facebook.com/%s' % str(user_id)
		data = {'method': 'delete', 'access_token': self.get_app_access_token()}
		resp = self.pool.request('GET', url, data)
		if resp.status == 200:
			return True
		else:
			raise FacebookAPIError("Could not complete API request: " + resp.data)

	def delete_test_users(self):
		"""Deletes all test users associated with application"""
		users = self.get_test_users()
		for u in users:
			self.delete_test_user(u['id'])

	def get_profile_picture(self, access_token, uid):
		"""Returns user's profile picture"""
		url = 'https://graph.facebook.com/%s/albums?access_token=%s' % (uid, access_token)
		try:
			resp = self.pool.request('GET', url)
			data = json.loads(resp.data)
			album_resp = self.pool.request('GET', 'https://graph.facebook.com/%s?access_token=%s' % (data['data'][0]['cover_photo'], access_token))
			album_data = json.loads(album_resp.data)
			img_url = album_data['source']
			img_resp = self.pool.request('GET', img_url)
			if img_resp.status==200 and img_resp.headers['content-type'] in ('image/jpeg','image/png','image/gif','image/jpg'):
				return (img_url.rsplit('/',1)[1], ContentFile(img_resp.data))
		except (HTTPError, KeyError, IndexError):
			raise FacebookAPIError("Could not fetch user profile picture!")

		return None


	def get_user_friends(self, user):
		url = 'https://graph.facebook.com/%s/friends' % user['id']
		data = {'access_token': user['access_token']}
		resp = self.pool.request('GET', url, data)
		if resp.status == 200:
			return json.loads(resp.data)['data']
		else:
			raise FacebookAPIError("Could not complete API request: " + resp.data)

	def friend_test_users(self, user, user2):
		url = 'https://graph.facebook.com/%s/friends/%s' % (str(user['id']), str(user2['id']))
		data = {'method': 'post', 'access_token': user['access_token']}
		resp = self.pool.request('GET', url, data)
		if resp.status!=200 or resp.data!='true':
			raise FacebookAPIError("Could not complete API request: " + resp.data)

		url = 'https://graph.facebook.com/%s/friends/%s' % (str(user2['id']), str(user['id']))
		data = {'method': 'post', 'access_token': user2['access_token']}
		resp = self.pool.request('GET', url, data)
		if resp.status!=200 or resp.data!='true':
			raise FacebookAPIError("Could not complete API request: " + resp.data)
		return True


