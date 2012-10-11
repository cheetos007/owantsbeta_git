import random
import urlparse
import urllib3
from urllib3.exceptions import HTTPError, TimeoutError, MaxRetryError

from django.utils import simplejson
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.utils import importlib
from django.utils.text import truncate_words

from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.helpers import ThumbnailError

#for find_images helper function (also used to test what images are supported)
SIZE_LIMITS = {'bmp':200, 'png': 10, 'jpeg': 5, 'gif': 10, 'other': 25}


def get_domain_name(url):
	"""
	Returns domain name without WWW from given url.
	e.g. 
	get_domain_name('http://www.example.org') -> example.org
	get_domain_name('http://example.org/?q=123') -> example.org
	"""
	netloc = urlparse.urlparse(url).netloc
	if netloc[0:3]=="www":
		return netloc[4:]
	else:
		return netloc

def prepare_json_list(pins):
	"""
	Return list of dictionaries describing pins. This should be used when returning pins in JSON.
	"""
	pin_list = []
	for p in pins:
		if hasattr(p, 'is_advertisment'):
			data = {'content': p.get_advertisment()}
		else:
			try:
				image = get_thumbnail(p.get_image(), '266', crop='center')
				im = {'url': image.url, 'width': image.width, 'height': image.height}
			except ThumbnailError:
				continue
			comments = []
			for c in p.comments:
				if c.user:
					try:
						c_image = get_thumbnail(c.user.get_profile().image, '30x30', crop='center')
						c_im = {'url': c_image.url, 'width': c_image.width, 'height': c_image.height}
					except ThumbnailError:
						continue
				comments.append({'im': c_im,'comment': truncate_words(c.comment, 5)})
			data = {'pk': p.pk, 'absolute_url': p.get_absolute_url(),'popup_url': p.get_popup_url(), 'number_of_repins': p.get_number_of_repins(), 
			'number_of_likes': p.get_number_of_likes(), 'thumbnail': im ,
				'description': truncate_words(p.description, 15), 'comments': comments}
		pin_list.append(data)

	return pin_list

def is_ajax_request(request):
	return 'ajax' in request.GET

def process_pin_list_request(request, pins, template, extra = {}, pins_per_request=25):
	"""
	If this is AJAX request (GET['ajax'] exists), returns HttpResponse with pins filtered by start/per page parameters.
	It also injects one advertisment per page (if advertisments are defined)
	"""
	start = 0
	
	if is_ajax_request(request):
		start = int(request.GET['start'])
		pins = pins[start:start+pins_per_request].annotate_with_comments()
		pins = inject_advertisment(list(pins))
		pins = prepare_json_list(pins)
		return HttpResponse(simplejson.dumps({'status': 'ok', 'pins': pins}), mimetype='application/json')
	else:
		data = {}
		data.update(extra)
		pins = pins[0:25].annotate_with_comments()
		pins = inject_advertisment(list(pins))
		data.update({'pins': pins})
		return direct_to_template(request, template, data)


def inject_advertisment(pins):
	"""
	Takes a list of pins and injects single advertisment in random place (if there are any active advertisments at that time)
	"""
	#import here to avoid circular imports
	from pins.models import PinAdvertisment
	ad = PinAdvertisment.objects.get_active_advertisment()
	if ad and len(pins)>0:
		pins.insert(random.randint(0, len(pins)), ad)
	return pins


def get_affiliate_func():
	try:
		affiliate_links_processor = getattr(settings, 'AFFILIATE_LINKS_PROCESSOR', 'pins.affiliate_link_processors.simple_processor')
		module = affiliate_links_processor[0:affiliate_links_processor.rfind('.')]
		func = affiliate_links_processor[affiliate_links_processor.rfind('.')+1:]
		m = importlib.import_module(module)

		return getattr(m, func)
	except (AttributeError, ImportError), e:
		raise Warning("Could not import AFFILIATE_LINKS_PROCESSOR, pin target URLs won't be processed.")



def find_images(soup, page_url):
	"""
	Returns all matching images from BeautifulSoup object soup.
	Matching images means, returning images which are larger than certain filesize.
	"""
	#get 10 first images which are larger than size limits (in KiB)
	
	images = []
	pool = urllib3.PoolManager()

	for img in soup.findAll('img'):
		src = img.get('src')
		if src:
			parsed = urlparse.urlparse(src)
			page_url_parsed = urlparse.urlparse(page_url)
			netloc = parsed.netloc or page_url_parsed.netloc
			scheme = parsed.scheme or page_url_parsed.scheme

			src_url = urlparse.urlunparse(urlparse.ParseResult(scheme=scheme, netloc=netloc, path=parsed.path, 
				params=parsed.params, query=parsed.query, fragment=parsed.fragment))
			
			try:

				#perform a HEAD request against URL to find out size of image
				request = pool.request('HEAD', src_url, timeout=2, retries=3, redirect=False)
				if request.status!=200 or not 'content-length' in request.headers:
					continue
				length = int(request.headers['content-length'])/1024
				content_type = request.headers['content-type'].split('/')[1]
				if (content_type in SIZE_LIMITS.keys() and length<SIZE_LIMITS[content_type]) \
						or (not content_type in SIZE_LIMITS.keys() and length < SIZE_LIMITS['other']):
					continue
				
				images.append(src_url)
				if len(images)==10:
					break
			except (HTTPError, MaxRetryError, TimeoutError):
				continue
	return images