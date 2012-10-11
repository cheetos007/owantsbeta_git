from django.shortcuts import get_object_or_404

from pins.models import Category, Pin
from pins.helpers import process_pin_list_request


def single_category(request, pk, slug):
	category = get_object_or_404(Category, pk=pk, is_active=True)
	
	if request.user.is_authenticated():
		pins = Pin.objects.latest_pins_for_user(request.user, category=pk)
		if pins.count() == 0:
			pins = Pin.objects.latest_pins(category=pk)
	else:
		pins = Pin.objects.latest_pins(category=pk)

	return process_pin_list_request(request, pins, 'pins/categories/single_category.html', {'category': category})