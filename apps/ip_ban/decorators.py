from ip_ban import is_request_banned
from django.views.generic.simple import direct_to_template

def prohibit_banned_access(func):
	"""
	Decorator for views. It assumes that first argument is called request, and 
	uses ip_ban.is_request_banned to determine if request is banned.
	If it is, it returns HttpResponse instead of executing original view code.
	"""
	def _inner(request, *args,**kwargs):
		if is_request_banned(request):
			return direct_to_template(request, 'ip_ban/banned.html')
		return func(request, *args, **kwargs)
	return _inner