"""
Affiliate link processor is a function which takes pin and request as an argument and returns URL 
which is used for outgoing links.

Processor can be activated by setting AFFILIATE_LINKS_PROCESSOR to dotted python path to function, e.g.
AFFILIATE_LINKS_PROCESSOR = 'pins.affiliate_link_processors.simple_processor'
"""

import urllib


def simple_processor(pin, request):
	"""
	Pass-through processor- returns pin's url.
	"""
	return pin.url

def advanced_example_processor(pin, request):
	"""
	Advanced example link processor- appends GET variables based on pin URL and current user id.
	Useful only as an example- please have a look at the source code.
	"""
	if pin.url:
		if request.user.is_authenticated():
			uid = request.user.pk
		else:
			uid = 0
		params = (('link', pin.url), ('uid', uid))
		return 'http://example.org/?%s' % urllib.urlencode(params)

	return ''