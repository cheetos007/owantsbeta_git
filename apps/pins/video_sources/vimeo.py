import re
import urllib2
import json

from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe

from pins.video_source_pool import RegexParser, parser_pool, VideoDescriptor, ParserException
from pins.video_source_pool import parser_pool

class VimeoVideoDescriptor(VideoDescriptor):

	def _get_thumbnail_url(self, size):
		assert size in ('medium','small', 'large')
		try:
			resp = urllib2.urlopen('http://vimeo.com/api/v2/video/%s.json' % self.video_id)
			resp_json = json.loads(resp.read())
			return resp_json[0]['thumbnail_%s' % size]
		except urllib2.HTTPError:
			raise ParserException("Cannot fetch data from Vimeo API for video id: %s" %
				self.video_id)

		except (IndexError, KeyError):
			raise ParserException("Thumbnail with size %s not found in response for video %s" 
				(size, self.video_id))

	def get_remote_thumbnail(self):
		return self._get_thumbnail_url('medium')

	def get_image_file(self):
		thumbnail_url = self._get_thumbnail_url('large')
		resp = urllib2.urlopen(thumbnail_url)

		assert(resp.headers['Content-Type'] in ('image/jpeg', 'application/octet-stream'))

		return ('vimeo_thumbnail.jpg', ContentFile(resp.read()))

	def get_video_markup(self, width, height):
		markup = """<iframe 
			src="http://player.vimeo.com/video/%s?title=0&amp;byline=0&amp;portrait=0&amp;color=136485" 
			width="%d" height="%d" frameborder="0" 
			webkitAllowFullScreen mozallowfullscreen allowFullScreen>
			</iframe>""" % (self.video_id, width, height )
		
		return mark_safe(markup)



class VimeoParser(RegexParser):
	parseable_tags = {'a':['href'],'iframe': ['src']}

	attribute_regex = re.compile(r"""(?:[\w]+\.)*		# Optional subdomains
	vimeo\.com		# Match vimeo.com
	(?:[\/\w]*\/videos?)?	# Optional video sub directory this handles groups links also
	\/			# Slash before Id
	([0-9]+)		# $1: VIDEO_ID is numeric""", re.VERBOSE)
	descriptor_class = VimeoVideoDescriptor

parser_pool.register_parser(VimeoParser)



