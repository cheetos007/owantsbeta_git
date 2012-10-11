from django import template
from django.core.urlresolvers import reverse
from django.template.base import TemplateSyntaxError

from site_settings.helpers import get_setting

register = template.Library()



class SettingNode(template.Node):
	def __init__(self, key, default=None, asvar=None):
		self.key = key
		self.default = default
		self.asvar = asvar

	def render(self, context):
		result = get_setting(self.key, self.default)
		if self.asvar:
			context[self.asvar] = result
			return ''
		else:
			return result


@register.tag
def site_setting(parser, token):
	"""
	This templatetag can be used to access site setting from templates.
	Usage: {% site_setting "site_name" %} or {% site_setting "nonexistant_setting" "default_return_value" %}
	"""
	bits = token.split_contents()
	if len(bits) < 2:
		raise TemplateSyntaxError("'%s' takes at least one argument"
								  " (setting key)" % bits[0])
	key = parser.compile_filter(bits[1]).var
	default = None
	asvar = None
	bits = bits[2:]
	if len(bits) >= 2 and bits[-2] == 'as':
		asvar = bits[-1]
		bits = bits[:-2]

	if len(bits)==1:
		default = bits[0]

	return SettingNode(key, default, asvar)

@register.inclusion_tag('site_settings/render_logo.html')
def site_logo(size="241x46"):
	return {'logo': get_setting('site_logo'), 'size': size}


