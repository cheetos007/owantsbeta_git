import os
import urlparse
from hashlib import md5

from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse

from menus.utils import _SimpleLanguageChanger, set_language_changer
from profiles import PROFILE_CACHE_TIMEOUT, PROFILE_CACHE_KEY
from ip_ban import is_request_banned


class LanguageChooserMiddleware():
	def process_request(self, request):
		set_language_changer(request, _SimpleLanguageChanger(request))
		
		host = request.get_host().lower().strip()
		if 'localhost' in host or not host or host=='testserver' or settings.INSIDE_TESTING:
			return None

		if host[:3] in ('www','dev'):
			host = host[4:]
		if ':' in host:
			host = host[:host.find(':')]

		host_hash = md5(host+'iddqd').hexdigest()


		return None


class IPBanMiddleware():
	def process_request(self, request):
		request.is_banned = is_request_banned(request)
		return None