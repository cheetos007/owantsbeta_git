"""owant it button: Overview.
	The owant it button consists of three main parts:
	1) Markup which is placed on target site where owant is to be added.
	2) JS include file which is included in the site where owant is added.
	3) View which is loaded in iframe. owant parameters (URL, default description, image url, button type) are passed in as GET parameters. The iframe renders button and pin count.
"""
import urlparse
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from pins.models import Pin
from pins.forms.button_forms import IframeParamsForm
from ip_ban.decorators import prohibit_banned_access

def button_js(request):
	"""
	This view renders the HTML/JavaScript template. Static file could be used, but as the site support multiple languages, and the domain name should not be hardcoded, 
	it's better to render JS via django template engine.
	"""
	return direct_to_template(request, "pins/button/button.html.js", mimetype="application/javascript")

def button_iframe(request):
	"""
	This view renders the HTML/JavaScript template. Static file could be used, but as the site support multiple languages, and the domain name should not be hardcoded, 
	it's better to render JS via django template engine.
	"""
	form = IframeParamsForm(data=request.GET)
	if form.is_valid():
		params = form.cleaned_data
		show_count = params['button_type']!='none'
		pin_count = Pin.objects.get_pin_count_by_url(params['image_url'])
		pin_button_url = request.build_absolute_uri(reverse('pin_button'))
	return direct_to_template(request, "pins/button/iframe.html", locals())

@prohibit_banned_access
def pin_button(request):
	"""
	This view renders popup window which is loaded when user selects the image to pin.
	The form itself is posted to py:func:`pins.views.finish_web_pin` view which handles the submission.
	"""
	image_src = request.GET['media']
	url = request.GET['src']

	return direct_to_template(request, "pins/button/pin_button.html", locals())