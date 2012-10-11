from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',
    url(r'^email/$', "invite_friends.views.email_invites", name="invite_friends_email"),
    url(r'^email/preview/$', "invite_friends.views.email_invites_preview", name="invite_friends_email_preview"),
    url(r'^email/accept/(?P<inv_type>[\w]+)/(?P<code>[\w\d]+)/$', "invite_friends.views.accept_invitation", name="invite_friends_accept"),

    url(r'^facebook/$', "invite_friends.views.invite_facebook_friends", name="invite_friends_facebook"),
    url(r'^facebook/sent/$', "invite_friends.views.sent_facebook_invites", name="sent_facebook_invites"),

)