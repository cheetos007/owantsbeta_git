from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

from comments.helpers import get_comments_for_obj

from pins.models import Pin, PinDomain
from pins.helpers import process_pin_list_request

def all_pins(request):
	pins = Pin.objects.latest_pins()
	return process_pin_list_request(request, pins, 'pins/index.html')

def single_pin(request, pin_pk, template='pins/single.html'):
	pin = get_object_or_404(Pin.objects.select_related('board', 'domain', 'board__category', 'source_pin','board__user','created_user'), pk=pin_pk, is_active=True,
			board__category__is_active=True, board__is_active=True)
	
	board_pins = pin.board.pin_set.filter(is_active=True).exclude(pk=pin_pk).select_related('source_pin')[:9]
	comment_list = get_comments_for_obj(pin)

	return direct_to_template(request, template, locals())

def single_domain(request, domain_name):
	domain = get_object_or_404(PinDomain, domain_name=domain_name)


def index(request):
	from pins.views.authenticated_views import followed_user_pins
	if request.user.is_authenticated():
		return followed_user_pins(request)
	else:
		return all_pins(request)

def videos(request):
	pins = Pin.objects.latest_video_pins()
	return process_pin_list_request(request, pins, 'pins/index.html')

