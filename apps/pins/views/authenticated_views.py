from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from ajax.decorators import json_response, login_required as ajax_login_required
from ajax.exceptions import AJAXError
from sorl.thumbnail import get_thumbnail

from pins.models import Pin, PinDomain, Board, Like
from pins.forms import UploadPinForm, AddPinForm, WebsiteURLForm, PinLikeForm
from pins.forms import get_pin_description_form, get_pin_url_form, get_repin_form
from pins.helpers import process_pin_list_request
import pins.signals

from ip_ban.decorators import prohibit_banned_access


@login_required
def followed_user_pins(request):
	pins = Pin.objects.latest_pins_for_user(request.user)
	if pins.count() == 0:
		pins = Pin.objects.latest_pins()

	extra = {'showing_following_pins': True}

	return process_pin_list_request(request, pins, 'pins/index.html', extra)

@prohibit_banned_access
@login_required
def pin_it(request):
	form = AddPinForm(data=request.POST or None, files=request.FILES or None)
	if form.is_valid():
		pin = form.save()
		messages.success(request, _('Pin uploaded successfully!'))
		return redirect("single_pin", pin.pk)

	boards = request.user.board_set.filter(is_active=True)
	return direct_to_template(request, "pins/pin_it.html", locals())


@prohibit_banned_access	
@login_required
def finish_pin(request):
	pin = get_object_or_404(Pin, pk=request.POST['pin_pk'], created_user=request.user)
	form = get_pin_description_form(request.user)(request.POST, instance=pin)
	if form.is_valid():
		pin = form.save(commit=False)
		pin.is_active = True
		pin.save()
		pins.signals.pin_finished.send_robust(finish_pin, instance=pin)
		messages.success(request, _('Pin uploaded successfully!'))
		return redirect("single_pin", pin.pk)
	else:
		messages.error(request, _('Could not upload pin!'))
		return redirect("pin_it")

@prohibit_banned_access
@login_required
def finish_web_pin(request, success_urlname = "single_pin", pin_source="url"):
	"""
	This view receives form's data from pin bookmarklet and "Pin from URL" feature.
	"""
	form = get_pin_url_form(request.user)(request.POST)
	if form.is_valid():
		pin = form.save(commit=False)
		pin.is_active = True
		pin.pin_source = pin_source
		pin.save()
		pins.signals.pin_finished.send_robust(finish_web_pin, instance=pin)
		messages.success(request, _('Pin created successfully!'))
		return redirect(success_urlname, pin.pk)
	else:
		messages.error(request, _('Could not upload pin!'))
		return redirect("pin_it")

@prohibit_banned_access
@login_required
def finish_web_owant(request, success_urlname = "single_pin", pin_source="url", owant_type="want"):
    """
     This view receives form's data from pin bookmarklet and "Pin from URL" feature.
     """
    form = get_pin_url_form(request.user)(request.POST)
    if form.is_valid():
        pin = form.save(commit=False)
        pin.is_active = True
        pin.pin_source = pin_source
        pin.owant_type = owant_type
        pin.save()
        pins.signals.pin_finished.send_robust(finish_web_pin, instance=pin)
        messages.success(request, _('Pin created successfully!'))
        return redirect(success_urlname, pin.pk)
    else:
        messages.error(request, _('Could not upload pin!'))
        return redirect("pin_it")


@login_required
def delete_pin(request, pin_pk):
	"""
	View that handles deletion of pin.
	"""
	pin = get_object_or_404(Pin, pk=pin_pk, created_user=request.user)
	if request.method=='POST' and 'ok' in request.POST:
		pin.is_active = False
		pin.save()
		messages.success(request, _('Pin deleted successfully!'))
		return redirect("home")
	return direct_to_template(request, "pins/delete_pin.html", locals())

@login_required
def edit_pin(request, pin_pk):
	pin = get_object_or_404(Pin, pk=pin_pk, created_user=request.user, 
		is_active=True, board__is_active=True, board__category__is_active=True)
	form = get_pin_description_form(request.user)(request.POST or None, instance=pin)
	if form.is_valid():
		pin = form.save(commit=False)
		pin.is_active = True
		pin.save()
		messages.success(request, _('Pin edited successfully!'))
		return redirect("single_pin", pin.pk)
	return direct_to_template(request, "pins/edit_pin.html", locals())

@csrf_exempt
@prohibit_banned_access
@login_required
def finish_repin(request):
	form = get_repin_form(request.user)(request.POST or None)
	if form.is_valid():
		pin = form.save()
		pins.signals.pin_finished.send_robust(finish_web_pin, instance=pin)
		messages.success(request, _('Pin repinned successfully!'))
		return redirect("single_pin", pin.pk)
	else:
		messages.fail(request, _('Could not repin the pin'))
		return redirect("home")

@csrf_exempt
@prohibit_banned_access
@ajax_login_required
@json_response('application/json')
def like_pin(request):
	"""
	AJAX view which increments number of likes for pin and returns the new number of likes.
	"""
	form = PinLikeForm(request.POST or None)
	if form.is_valid():
		pin = form.cleaned_data['pin']
		Like.objects.like_pin(pin, request.user)
		pin = Pin.objects.select_related().get(pk=pin.pk)
		return {'number_of_likes':pin.get_number_of_likes(),}
	else:
		raise AJAXError(_("Could not like the pin!"))


	
	

	