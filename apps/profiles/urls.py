from django.conf.urls.defaults import *
from django.conf import settings

#pin urls
urlpatterns = patterns('',
    url(r'^edit/$', "profiles.views.edit_profile", name="edit_profile"),
    url(r'^user/(?P<username>[\w.]+)/$', "profiles.views.view_profile", name="view_profile"),
    url(r'^edit/upload_image/$', "profiles.views.upload_profile_image", name="upload_profile_image"),
    url(r'^delete/$', "profiles.views.delete_profile", name="delete_profile"),
    url(r'^following/$', 'profiles.views.following_users_list', name='following_users'),
    url(r'^followers/$', 'profiles.views.follower_users_list', name='follower_users'),

)