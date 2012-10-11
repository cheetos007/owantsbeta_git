from comments.forms import ObjectCommentForm
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

def get_model():
	return Comment

def get_form():
    return ObjectCommentForm

from comments.moderator import *

def comment_attach_message(sender, comment, request, *args, **kwargs):
    message = _('Your comment was posted.')
    messages.add_message(request, messages.SUCCESS, message)
    
#comment_was_posted.connect(comment_attach_message, get_model())