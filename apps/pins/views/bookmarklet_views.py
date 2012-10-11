"""Pin it bookmarklet: Overview.
	The bookmarklet itself is a snippet of JavaScript, which injects py:func:`pins.views.bookmarklet_views.bookmarklet_js` file into the current window (target page).
	The JS file adds a CSS stylesheet and creates overlay, which lists the images found in site. Images are shown ordered by size.
	When user clicks on image, a popup is opened which shows py:func:`pins.views.bookmarklet_views.pin_bookmarklet` view. 
	This view allows user to enter description and select board- after that, the data is posted to the same view which handles pin from url functionality. 
"""
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from pins.models import Pin
from ip_ban.decorators import prohibit_banned_access

def bookmarklet_js(request):
	"""
	This view renders the HTML/JavaScript template. Static file could be used, but as the site support multiple languages, and the domain name should not be hardcoded, 
	it's better to render JS via django template engine.
	"""
	return direct_to_template(request, "pins/bookmarklet/bookmarklet.html.js", mimetype="application/javascript")

#unfortunately, this URL has to be hardcoded because decorator strictly wants URL not urlname
@prohibit_banned_access
@login_required(login_url='/account/login/popup/')
def pin_bookmarklet(request):
	"""
	This view renders popup window which is loaded when user selects the image to pin.
	The form itself is posted to py:func:`pins.views.finish_web_pin` view which handles the submission.
	"""
	image_src = request.GET.get('media', '');
	url = request.GET['src'];
	video_id = request.GET.get('video_id', '');
	parser = request.GET.get('parser','');
	return direct_to_template(request, "pins/bookmarklet/pin_bookmarklet.html", locals())

#unfortunately, this URL has to be hardcoded because decorator strictly wants URL not urlname
@prohibit_banned_access
@login_required(login_url='/account/login/popup/')
def own_bookmarklet(request):
    """
     This view renders popup window which is loaded when user selects the image to pin.
     The form itself is posted to py:func:`pins.views.finish_web_pin` view which handles the submission.
     """
    image_src = request.GET.get('media', '');
    url = request.GET['src'];
    video_id = request.GET.get('video_id', '');
    parser = request.GET.get('parser','');
    return direct_to_template(request, "pins/bookmarklet/own_bookmarklet.html", locals())

#unfortunately, this URL has to be hardcoded because decorator strictly wants URL not urlname
@prohibit_banned_access
@login_required(login_url='/account/login/popup/')
def want_bookmarklet(request):
    """
     This view renders popup window which is loaded when user selects the image to pin.
     The form itself is posted to py:func:`pins.views.finish_web_pin` view which handles the submission.
     """
    image_src = request.GET.get('media', '');
    url = request.GET['src'];
    video_id = request.GET.get('video_id', '');
    parser = request.GET.get('parser','');
    return direct_to_template(request, "pins/bookmarklet/want_bookmarklet.html", locals())


@login_required(login_url='/account/login/popup/')
def bookmarklet_finished(request, pin_pk):
	"""
	This view shows the success page after pin has been submitted via bookmarklet.
	"""
	pin = get_object_or_404(Pin, pk = pin_pk)
	return direct_to_template(request, "pins/bookmarklet/finished.html", locals())