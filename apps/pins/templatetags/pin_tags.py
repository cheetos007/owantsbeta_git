import re

from django import template
from django.core.urlresolvers import reverse
from django.template.defaulttags import URLNode, url

from django.template.base import TemplateSyntaxError
from pins.models import Category, Board, Pin, Like

register = template.Library()


kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


@register.inclusion_tag('pins/categories_dropdown.html')
def pin_categories_dropdown():
	return {'categories': Category.objects.get_list_for_dropdown()}


class ActiveUrlNode(template.Node):
	def __init__(self, url):
		self.url = url

	def render(self, context):
		if reverse(self.url) == context['request'].path:
			return 'active'
		return ''

@register.tag
def is_active_url(parser, token):
	"""
	Returns "active" if request.path == reverse(url).
	Allows to add .active to active links/url's.

	Usage:
		<li class="{% is_active_url "objects" %}"><a href="{% url "objects" %}"></li>
	Warning- argument will be passed through django.core.urlresolvers.reverse so it better be valid URL
	"""

	bits = token.split_contents()
	return ActiveUrlNode(bits[1])


@register.inclusion_tag('pins/rooms/user_boards.html', takes_context=True)
def user_boards(context, user):
	ctx = context
	ctx.update({'boards': Board.objects.get_user_public_boards(user),
				'number_of_pins': Pin.objects.get_number_of_pins_for_user(user),
				'number_of_likes': Like.objects.get_number_of_likes_for_user(user)})
	return ctx

@register.inclusion_tag('pins/_welcome_user_pins.html')
def user_pins(user, num_pins = 8):
	return {'pins': Pin.objects.filter(board__user=user, is_active=True, 
		board__is_active=True, board__category__is_active=True).order_by('?').select_related()[:num_pins-1]}


class AbsoluteURLNode(URLNode):
    def render(self, context):
        path = super(AbsoluteURLNode, self).render(context)
        return context['request'].build_absolute_uri(path)


@register.tag
def absolute_url(parser, token):
    """
    Returns an absolute (no, I mean really absolute, as in having domain name) URL matching given view with its parameters.

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% url path.to.some_view arg1 arg2 %}

        or

        {% url path.to.some_view name1=value1 name2=value2 %}

    The first argument is a path to a view. It can be an absolute python path
    or just ``app_name.view_name`` without the project name if the view is
    located inside the project.  Other arguments are comma-separated values
    that will be filled in place of positional and keyword arguments in the
    URL. All arguments for the URL should be present.

    For example if you have a view ``app_name.client`` taking client's id and
    the corresponding line in a URLconf looks like this::

        ('^client/(\d+)/$', 'app_name.client')

    and this app's URLconf is included into the project's URLconf under some
    path::

        ('^clients/', include('project_name.app_name.urls'))

    then in a template you can create a link for a certain client like this::

        {% url app_name.client client.id %}

    The URL will look like ``/clients/client/123/``.
    """

    import warnings
    warnings.warn('The syntax for the url template tag is changing. Load the `url` tag from the `future` tag library to start using the new behavior.',
                  category=PendingDeprecationWarning)

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    # Backwards compatibility: check for the old comma separated format
    # {% url urlname arg1,arg2 %}
    # Initial check - that the first space separated bit has a comma in it
    if bits and ',' in bits[0]:
        check_old_format = True
        # In order to *really* be old format, there must be a comma
        # in *every* space separated bit, except the last.
        for bit in bits[1:-1]:
            if ',' not in bit:
                # No comma in this bit. Either the comma we found
                # in bit 1 was a false positive (e.g., comma in a string),
                # or there is a syntax problem with missing commas
                check_old_format = False
                break
    else:
        # No comma found - must be new format.
        check_old_format = False

    if check_old_format:
        # Confirm that this is old format by trying to parse the first
        # argument. An exception will be raised if the comma is
        # unexpected (i.e. outside of a static string).
        match = kwarg_re.match(bits[0])
        if match:
            value = match.groups()[1]
            try:
                parser.compile_filter(value)
            except TemplateSyntaxError:
                bits = ''.join(bits).split(',')

    # Now all the bits are parsed into new format,
    # process them as template vars
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return AbsoluteURLNode(viewname, args, kwargs, asvar, legacy_view_name=True)
url = register.tag(url)


@register.simple_tag(takes_context=True)
def pin_target_url(context, pin, asvar=None):
    if pin:
        url = pin.get_target_url(context['request'])
    else:
        url = ''
    if asvar:
        context[asvar] = url
        return ''
    else:
        return url