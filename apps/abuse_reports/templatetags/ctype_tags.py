from django import template

from pins.models import Category, Board, Pin
from django.contrib.contenttypes.models import ContentType

register = template.Library()


class CTypeUrlNode(template.Node):
    def __init__(self, obj, asvar=None):
        self.obj = template.Variable(obj)
        self.asvar = asvar

    def render(self, context):
        obj = self.obj.resolve(context)
        ctype = ContentType.objects.get_for_model(obj.__class__).pk
        if self.asvar:
            context[self.asvar] = ctype
            return ''
        return ctype


@register.tag
def content_type(parser, token):
    """
    Returns content type pk for given model.
    This should only be useful when used as follows {% content_type obj as somevar %}
    """

    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("'%s' takes at least one argument"
                                  " (object)" % bits[0])
    obj = bits[1]
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
    

    return CTypeUrlNode(obj, asvar)