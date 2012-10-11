from django.template import Context
from django.template.loader import get_template
from django import template


register = template.Library()


@register.filter
def facebook_profile_url(user):
	"""Return Facebook profile url for given user.
	If user's account is not associated with Facebook, empty string is returned"""
	social_auth = user.social_auth.filter(provider='facebook')
	try:
		if len(social_auth)>0:
			return 'https://www.facebook.com/%s' % social_auth[0].extra_data['id']
	except (KeyError, ValueError):
		pass
	return ''

@register.filter
def twitter_profile_url(user):
	"""Return Twitter profile url for given user.
	If user's account is not associated with Facebook, empty string is returned"""
	social_auth = user.social_auth.filter(provider='twitter')
	try:
		if len(social_auth)>0:
			return 'https://twitter.com/account/redirect_by_id?id=%d' % social_auth[0].extra_data['id']
	except (KeyError, ValueError):
		pass
	return ''
