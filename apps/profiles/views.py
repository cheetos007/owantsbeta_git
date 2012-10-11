from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from ajax.decorators import json_response, login_required as ajax_login_required
from ajax.exceptions import AJAXError
from sorl.thumbnail import get_thumbnail

from profiles.forms import get_profile_form_class, ProfileImageForm, get_password_form

from social_auth.views import disconnect

from pins.follow import follow

@login_required
def edit_profile(request):
	form_class = get_profile_form_class(request.user)
	form = form_class(data=request.POST or None, files=request.FILES or None)
	if form.is_valid():
		form.save()

		#call social_auth.views.disconnect if user want's to de-associate his/her social auth accounts
		if not form.cleaned_data['link_twitter']:
			disconnect(request, 'twitter')

		if not form.cleaned_data['link_facebook']:
			disconnect(request, 'facebook')

		messages.success(request, _('Your profile has been updated.'))
		return redirect(request.user.get_absolute_url())

	return direct_to_template(request, 'profiles/edit_profile.html', locals())


def view_profile(request, username):
	user = get_object_or_404(User, username=username, is_active=True)
	profile = user.get_profile()

	return direct_to_template(request, 'profiles/view_profile.html', locals())

@csrf_exempt
@ajax_login_required
@json_response('text/html')
def upload_profile_image(request):
	form = ProfileImageForm(files=request.FILES or None)
	if form.is_valid():
		img = form.save(request.user.get_profile())
		return {'thumbnail': get_thumbnail(img, "160").url}
	else:
		raise AJAXError(_("Uploaded file is not valid!"))


@login_required
def delete_profile(request):
	PasswordForm = get_password_form(request.user)
	form = PasswordForm(request.POST or None)
	if form.is_valid():
		request.user.delete()
		messages.success(request, _('Your account has been deleted permanently. We\'re sorry to let you go...'))
		return redirect('home')

	return direct_to_template(request, 'profiles/delete_confirmation.html', locals())



@login_required
def following_users_list(request):
	user_list = User.objects.filter(pk__in=follow.get_user_following(request.user.pk))
	profile = request.user.get_profile()
	return direct_to_template(request, 'profiles/follow/following_users.html', locals())

@login_required
def follower_users_list(request):
	user_list = User.objects.filter(pk__in=follow.get_user_followers(request.user.pk))
	profile = request.user.get_profile()
	return direct_to_template(request, 'profiles/follow/follower_users.html', locals())
	



