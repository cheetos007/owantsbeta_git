from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template

from actstream.models import actor_stream, user_stream

from pins.follow import follow
from pins.models import Board


register = template.Library()


@register.inclusion_tag('profiles/activities.html')
def action_list(user, limit=15):
	return {'action_list': actor_stream(user)[:limit]}

@register.inclusion_tag('profiles/activities.html')
def activity_stream_for_user(user, limit=10):
	return {'action_list': user_stream(user)[:limit]}


@register.filter
def is_following_user(user, followee):
	is_authenticated = getattr(user, 'is_authenticated', None)
	if (is_authenticated and is_authenticated()) or not is_authenticated:
		user_pk = getattr(user, 'pk', user)
		followee_pk = getattr(followee, 'pk', followee)
		return follow.is_following_user(user_pk, followee_pk)


@register.filter
def is_following_board(user, board):
	is_authenticated = getattr(user, 'is_authenticated', None)
	if (is_authenticated and is_authenticated()) or not is_authenticated:
		user_pk = getattr(user, 'pk', user)
		board_pk = getattr(board, 'pk')
		return (follow.is_following_user(user_pk, board.user.pk) and not follow.is_unfollowing_board(user_pk, board_pk)) \
				 or follow.is_following_board(user_pk, board_pk)


@register.filter
def number_of_followers(user):
	return len(follow.get_user_followers(user.pk))

@register.filter
def number_of_following(user):
	return len(follow.get_user_following(user.pk))


class BoardContentTypeNode(template.Node):

    def __init__(self, *args):
        self.args = args

    def render(self, context):
        context[self.args[-1]] = ContentType.objects.get_for_model(Board)
        return ''

@register.tag
def get_board_contenttype(parser, token):
    return BoardContentTypeNode(*token.split_contents())