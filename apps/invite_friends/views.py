from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.contrib import messages
from django.contrib.sites.models import Site
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django.template import Context
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

from ajax.decorators import json_response, login_required as ajax_login_required

from social_auth.models import UserSocialAuth

from invite_friends.forms import email_invite_form_factory, PersonalNoteForm, BaseEmailInviteFormSet
from invite_friends.models import EmailInvite, FacebookInvite
from invite_friends.settings import EMAIL_INVITE_BODY_TEMPLATE, EMAIL_INVITE_SUBJECT_TEMPLATE
from invite_friends.facebook import facebook_factory, FacebookAPIError

@login_required
def email_invites(request):
	form_class = email_invite_form_factory(request.user)
	formset_class = modelformset_factory(EmailInvite, form=form_class, extra=4, formset=BaseEmailInviteFormSet)
	personal_note_form = PersonalNoteForm(request.POST or None)
	formset = formset_class(request.POST or None)
	if formset.is_valid():
		invites = formset.save(commit=False)
		if personal_note_form.is_valid():
			note = personal_note_form.cleaned_data['personal_note']
		for i in invites:
			i.personal_note = note
			i.save()

		messages.success(request, _('Invites sent successfully!'))
		return redirect("home")


	return direct_to_template(request, 'invite_friends/email_invite.html', locals())

@login_required
def email_invites_preview(request):
	"""
	Useful for design changes- renders invite e-mail template in browser.
	"""
	if 'inv_pk' in request.GET:
		invite = get_object_or_404(EmailInvite, pk=request.GET['inv_pk'])
	else:
		invite = EmailInvite(user=request.user, email='test@example.org')
	site = Site.objects.get_current()
	context = Context(locals())
	subject = get_template(EMAIL_INVITE_SUBJECT_TEMPLATE).render(context)
	return direct_to_template(request, EMAIL_INVITE_BODY_TEMPLATE, locals())

def accept_invitation(request, inv_type, code):
	"""
	View that redirects to sign up view with correct variables set.
	inv_type- invitation model class name (e.g. EmailInvite)
	code - invitation code (must exist in database)
	"""
	pass

@login_required
def invite_facebook_friends(request):
	try:
		auth = UserSocialAuth.objects.get(user=request.user, provider='facebook')
		fb = facebook_factory()
		cache_key = 'user_facebook_friends:%d:%s' % (request.user.pk, auth.extra_data['id'])
		friends_list = cache.get(cache_key)
		invited_fb_ids = FacebookInvite.objects.filter(user=request.user).values_list('facebook_user_id', flat=True)
		if friends_list is None:
			friends_list = fb.get_user_friends(auth.extra_data)
			cache.set(cache_key, friends_list, 3600)
		friends_list_json = json.dumps([f['id'] for f in friends_list if not f['id'] in invited_fb_ids])
	except UserSocialAuth.DoesNotExist:
		#user has not logged in via Facebook
		auth_url = reverse('socialauth_associate_begin', kwargs={'backend': 'facebook'})
	except FacebookAPIError:
		#most likely user's auth token has expired
		auth_url = reverse('socialauth_begin', kwargs={'backend': 'facebook'})
	site = Site.objects.get_current()
	
	invite = FacebookInvite.objects.get_or_create(user=request.user, sent=True)[0]
	return direct_to_template(request, 'invite_friends/facebook_invite.html', locals())

@csrf_exempt
@ajax_login_required
@json_response('application/json')
def sent_facebook_invites(request):
	fb_ids = request.POST['fb_ids'].split(',')
	personal_note = request.POST['note']
	for fb_id in fb_ids:
		FacebookInvite.objects.create(user=request.user, facebook_user_id=fb_id, sent=False, personal_note=personal_note)
	return {'status': 'ok'}



	