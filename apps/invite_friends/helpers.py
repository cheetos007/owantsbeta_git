from urllib import urlencode
from invite_friends import models
from actstream import actions

def get_invite_parameters(request):
	"""
	Checks if request.GET contains invitation parameters. 
	If it does, returns GET data to use in links to other signup methods
	"""

	if 'inv_type' in request.GET and 'code' in request.GET:
		request.session['inv_type'] = request.GET['inv_type']
		request.session['code'] = request.GET['code']
		return '?'+urlencode({'inv_type': request.GET['inv_type'], 'code': request.GET['code']})


	return ''

def accept_invite(request, new_user):
	"""
	Mark invite as accepted and set up following relationships for both users.
	"""
	inv = get_invite_from_request(request)
	if inv:
		inv.accept_invitation(request, new_user)
		actions.follow(new_user, inv.user)
		actions.follow(inv.user, new_user)
		
def get_invite_from_request(request):
	try:
		if 'inv_type' in request.GET:
			inv_type = request.GET['inv_type']
			code = request.GET['code']
		else:
			inv_type = request.session['inv_type']
			code = request.session['code']
		model_class = getattr(models, inv_type)
		return model_class.objects.get(code=code)
	except (KeyError, AttributeError):
		return None

