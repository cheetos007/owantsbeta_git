"""
Reusable app to deny access to users identified by IP address.
The IP addresses are specified in django's admin, and one can specify a range of IP addresses to ban.

Usage::

 from ip_ban import is_request_banned

 def someview(request):
	 if is_request_banned(request):
		 #show some error message to user
	 else:
		 #execute normal code

Usage with decorator::

 from ip_ban.decorators import prohibit_banned_access

 @prohibit_banned_access
 def someview(request):
	 #normal view code

Decorator renders ip_ban/banned.html template if the IP address is banned.
"""

from ip_ban.models import BanIP
from django.core.cache import cache

def is_request_banned(request):
	"""
	Returns True if request's IP is in a list of banned IP's.
	Otherwise, False is returned.
	"""
	banned_ips = cache.get('banned_ips', None)
	if banned_ips is None:
		banned_ips = []
		for ip in BanIP.objects.all():
			for n in ip.network:
				banned_ips.append(str(n))
		cache.set('banned_ips', banned_ips)
	return request.META['REMOTE_ADDR'] in banned_ips