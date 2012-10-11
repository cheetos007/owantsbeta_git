from django.contrib.comments.moderation import CommentModerator, moderator
from pins.models import Pin 
from ip_ban import is_request_banned

class PinCommentModerator(CommentModerator):
    def allow(self, comment, content_object, request):
    	return not is_request_banned(request)

moderator.register(Pin, PinCommentModerator)