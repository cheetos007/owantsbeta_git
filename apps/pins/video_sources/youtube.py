import re
import urllib2

from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe

from pins.video_source_pool import RegexParser, parser_pool, VideoDescriptor
from pins.video_source_pool import parser_pool

class YoutubeVideoDescriptor(VideoDescriptor):

	def get_remote_thumbnail(self):
		return u'http://img.youtube.com/vi/%s/default.jpg' % self.video_id

	def get_image_file(self):
		resp = urllib2.urlopen('http://img.youtube.com/vi/%s/hqdefault.jpg' % self.video_id)
		assert(resp.headers['Content-Type']=='image/jpeg')
		return ('hqdefault.jpg', ContentFile(resp.read()))

	def get_video_markup(self, width, height):
		markup = """<iframe class="youtube-player" 
			type="text/html" width="%d" height="%d" 
			src="http://www.youtube.com/embed/%s" frameborder="0">
			</iframe>""" % (width, height, self.video_id)
		
		return mark_safe(markup)



class YoutubeParser(RegexParser):
	parseable_tags = {'a':['href'],'iframe': ['src'], 'param':['movie'], 'embed':['src']}

	attribute_regex = re.compile(r'(?:youtube(?:-nocookie)?\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/ ]{11})')
	descriptor_class = YoutubeVideoDescriptor

parser_pool.register_parser(YoutubeParser)



