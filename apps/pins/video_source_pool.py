"""This module provides a pluggable interface for video sources. Most promintent video
source could be Youtube, for example. Each parser provides a list of tags parser is interested in.
These lists from all active (registered) parsers are combined in a single filter which is then used 
to filter tags from BeautifulSoup. It should be more efficient than parsing all tags and passing them to
all video source parsers.
Each parser class defines it's own HTML output for video. It may also register media (JS) which will be loaded in 
the page where the HTML output is displayed.
Each parser has to provide two properties for matching videos- video id and extra_data (dictionary, optional).

For the description of parser methods, please see BaseParser class."""

import re
from BeautifulSoup import BeautifulSoup

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import URLValidator




validate_url = URLValidator(verify_exists=False)

class ParserPool(object):
	def __init__(self):
		self.parsers = {}
		self.discovered = False

	def discover_parsers(self):
		if self.discovered:
			return
		self.discovered = True

		#avoid circular imports
		from cms.utils.django_load import load
		load('video_sources')

	def register_parser(self, parser):
		"""
		Registers the given parser(s).

		"""

		if not issubclass(parser, BaseParser):
			raise ImproperlyConfigured(
				"Video source parsers must be subclasses of BaseParser, %r is not."
				% parser
			)
		parser_name = parser.__name__
		if parser_name not in self.parsers:
			parser.value = parser_name
			self.parsers[parser_name] = parser()

	def unregister_parser(self, parser):
		"""
		Unregisters the given parser(s).

		If a parser isn't already registered, this will raise KeyError.
		"""
		try:
			parser_name = parser.__name__
		except AttributeError:
			parser_name = parser
		if parser_name not in self.parsers:
			raise KeyError(
				'The parser %r is not registered' % parser
			)
		del self.parsers[parser_name]

	def get_all_parsers(self):
		self.discover_parsers()
		return self.parsers.values()[:]


	def get_parser(self, name):
		"""
		Retrieve a plugin from the cache.
		"""
		self.discover_parsers()
		return self.parsers[name]

	def _parser_results(self, parser_class, bs_data):
		return parser_class.parse_tags(bs_data.findAll(parser_class.required_tag_names()))

	def get_parser_results(self, parser_name, data):
		"""Returns a list of VideoDescriptor subclass instances from single parser"""
		self.discover_parsers()
		data = self._prepare_data(data)
		return self._parser_results(self.get_parser(parser_name), BeautifulSoup(data))

	def get_results(self, data):
		self.discover_parsers()
		data = self._prepare_data(data)
		results = []
		search_tags = self._get_required_tags()
		bs_data = BeautifulSoup(data).findAll(search_tags)
		for p in self.parsers.values():
			results.extend(p.parse_tags(bs_data))

		return results

	def _get_required_tags(self):
		required_tags = []
		for p in self.parsers.values():
			required_tags.extend([t for t in p.required_tag_names() if not t in required_tags])
		return required_tags

	def _prepare_data(self, data):
		"""
		If video URL is passed in, it's converted to <a href="video_url"></a>.
		Otherwise, input is returned.
		"""
		try:
			validate_url(data)
			data = '<a href="%s"></a>' % data
		except ValidationError:
			pass

		return data

	def get_video_descriptor(self, parser, video_id):
		return self.get_parser(parser).create_descriptor(video_id)




parser_pool = ParserPool()

class VideoDescriptor(object):
	"""This class is used to represent individual matching result from parsers."""
	def __init__(self, parser, video_id, extra_data={}):
		self.parser = parser
		self.video_id = video_id
		self.extra_data = extra_data

	def get_remote_thumbnail(self):
		"""Returns an URL of remote thumbnail. It's used before pin is saved for preview purposes"""
		raise NotImplementedError("Subclasses should implement this method.")

	def get_image_file(self):
		"""Returns a tuple consisting of base file name (only filename, without path) and 
		file-like object of the local thumbnail for this video."""
		raise NotImplementedError("Subclasses should implement this method.")

	def get_video_markup(self, width, height):
		"""Returns HTML markup (with mark_safe applied) which should be used to render video player"""
		raise NotImplementedError("Subclasses should implement this method.")




class BaseParser(object):
	"""BaseParser is the base class for all parsers."""

	descriptor_class = VideoDescriptor

	def parse_tags(self, tags):
		"""
		This method should return a list of VideoDescriptor subclass instances for 
		matched videos in given list of BeautifulSoup tags
		"""

		raise NotImplementedError("Subclasses should implement this method")


	def required_tag_names(self):
		"""
		This method should return a list of tag names particular parser is interested in (e.g. ['a', 'iframe'])
		"""
		raise NotImplementedError("Subclasses should implement this method")

	def create_descriptor(self, video_id):
		return self.descriptor_class(self.__class__.__name__, video_id)


class RegexParser(BaseParser):
	"""
	RegexParser class provides a configurable superclass which should be suitable for most video source parsers.
	It provides a list of tags interested in, and their attributes. Matching tag attributes are matched against 
	single regular expression. If the regular expression matches, it's 1st group should contain video id.

	Subclasses should probably override descriptor_class, parseable_tas and attribute_regex.
	"""
	
	#dictionary of tags->[attribute_list] this parser is interested in
	parseable_tags = {'a':['href'],'iframe': ['src'], 'param':['movie'], 'embed':['src']}

	#attribute regex with at least one group which should match video id
	attribute_regex = re.compile('(.*)')

	#descriptor class which will be used to return matches
	descriptor_class = VideoDescriptor

	def parse_tags(self, tags):
		videos = []
		video_ids = []
		for t in tags:
			if hasattr(t, 'name') and t.name in self.parseable_tags:
				for a in self.parseable_tags[t.name]:
					attr_value = t.get(a)
					if attr_value:
						matches = self.attribute_regex.search(attr_value)
						if matches and len(matches.groups())>0:
							video_id = matches.group(1)
							if video_id not in video_ids:
								videos.append(self.create_descriptor(video_id))
								video_ids.append(video_id)
		return videos


	def required_tag_names(self):
		return self.parseable_tags.keys()


class ParserException(Exception):
	pass


