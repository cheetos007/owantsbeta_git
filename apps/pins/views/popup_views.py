from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
import urllib3
from urllib3.exceptions import HTTPError, TimeoutError, MaxRetryError
import urlparse

from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from ajax.decorators import json_response, login_required as ajax_login_required
from ajax.exceptions import AJAXError
from sorl.thumbnail import get_thumbnail

from pins.models import Pin, PinDomain
from pins.forms import UploadPinForm, AddPinForm, WebsiteURLForm
from pins.forms import get_pin_description_form, get_pin_url_form
from pins.helpers import find_images, SIZE_LIMITS

from pins.video_source_pool import parser_pool
from ip_ban.decorators import prohibit_banned_access

@csrf_exempt
@prohibit_banned_access
@ajax_login_required
@json_response('text/html')
def upload_pin(request):
	form = UploadPinForm(files=request.FILES or None)
	if form.is_valid():
		pin = form.save(commit=False)
		pin.is_active = False
		pin.save()
		return {'pin_pk':pin.pk, 
			'thumbnail': get_thumbnail(pin.image, "100x100", crop="center").url}
	else:
		raise AJAXError(_("Uploaded file is not valid!"))

@csrf_exempt
@prohibit_banned_access
@ajax_login_required
@json_response('application/json')
def website_media(request):
	"""
	Returns a list of media for given URL (from POST['url'])
	@TODO: We should be checking dimensions of images in URL and return only those 
	which are larger than n pixels.	However, if it needs to be done,
	it needs to be done in asynchronous/multithreaded fashion.

	For now, only images larger than 15KiB when lossy and 25KiB when lossless are returned.
	Returned structure is:
	{
	'images': ['http://example.org/image.jpeg',..],

	 'videos': [{'thumbnail':'<url of thumbnail shown to user>','parser':'<parser class name>',
				'video_id': '<video id>'}, 
				...]
	}
	"""
	form = WebsiteURLForm(request.POST or None)
	if form.is_valid():
		pool = urllib3.PoolManager(headers={'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'})
		url = form.cleaned_data['url']
		images = []
		website_request = pool.request('GET', url, timeout=4, retries=3)
		if website_request.status==200:
			content_type = website_request.headers['content-type'].split('/')[1]
			if content_type in SIZE_LIMITS.keys():
				#the given URL is image
				images.append(url)
			else:
				soup = BeautifulSoup(website_request.data)
				images.extend(find_images(soup, url))

			videos = parser_pool.get_results(url)
			if len(videos)==0:
				videos = parser_pool.get_results(website_request.data)

		return {'images': images, 'videos': convert_videos_to_json(videos)}
	else:
		raise AJAXError(msg=_("Could not fetch images."))



def convert_videos_to_json(videos):
	resp = []
	for v in videos:
		resp.append({'thumbnail': v.get_remote_thumbnail(), 'parser': v.parser, 
			'video_id': v.video_id})
	return resp

@ajax_login_required
@json_response('application/json')
def pin_information(request):
	pin = get_object_or_404(Pin, pk=request.GET['pin_pk'], is_active=True, 
		board__is_active=True, board__category__is_active=True)
	return {'description': pin.description, 'thumbnail': 
		get_thumbnail(pin.get_image(), "100x100", crop="center").url}
