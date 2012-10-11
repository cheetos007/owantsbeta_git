from django.conf.urls.defaults import *
from django.conf import settings

#pin urls
urlpatterns = patterns('',
    url(r'^all/$', "pins.views.all_pins", name="home"),
    url(r'^videos/$', "pins.views.videos", name="videos"),
    url(r'^pin/(?P<pin_pk>\d+)/$', "pins.views.single_pin", name="single_pin"),
    url(r'^pin/(?P<pin_pk>\d+)/popup/$', "pins.views.single_pin", name="single_pin_popup", kwargs={'template': 'pins/single_popup.html'}),
    url(r'^pin/(?P<pin_pk>\d+)/edit/$', "pins.views.edit_pin", name="edit_pin"),
    url(r'^pin/(?P<pin_pk>\d+)/delete/$', "pins.views.delete_pin", name="delete_pin"),
    url(r'^pin_it/$', "pins.views.pin_it", name="pin_it"),
    
    url(r'^finish_pin/$', "pins.views.finish_pin", name="finish_pin"),
    
    url(r'^like_pin/$', "pins.views.like_pin", name="like_pin"),
    url(r'^finish_web_pin/$', "pins.views.finish_web_pin", name="finish_web_pin"),

    
    url(r'^finish_repin/$', "pins.views.finish_repin", name="finish_repin"),
    url(r'^$', "pins.views.index", name="index"),
)

#pin popup urls
urlpatterns = urlpatterns + patterns('',
    url(r'^upload_pin/$', "pins.views.popup_views.upload_pin", name="upload_pin"),
    url(r'^pin_information/$', "pins.views.popup_views.pin_information", name="pin_information"),
    url(r'^website_media/$', "pins.views.popup_views.website_media", name="website_media"),
)

#board urls
urlpatterns = urlpatterns + patterns('',
	url(r'^rooms/$', "pins.views.boards", name="boards"),
	url(r'^rooms/add/$', "pins.views.add_board", name="add_board"),
    url(r'^rooms/(?P<board_pk>\d+)/edit/$', "pins.views.edit_board", name="edit_board"),
    url(r'^rooms/(?P<board_pk>\d+)/delete/$', "pins.views.delete_board", name="delete_board"),
	url(r'^rooms/(?P<board_pk>\d+)/(?P<slug>[\w\d-]+)/$', "pins.views.single_board", name="single_board"),

)

#welcome wizard urls
urlpatterns = urlpatterns + patterns('',
    url(r'^welcome-wizard/$', "pins.views.welcome_wizard", name="welcome_wizard"),
    url(r'^choose_people_to_follow/$', "pins.views.choose_people_to_follow", name="choose_people_to_follow"),
    url(r'^create_initial_boards/$', "pins.views.create_initial_boards", name="create_initial_boards"),
)

#bookmarklet urls
urlpatterns = urlpatterns + patterns('',
    url(r'^bookmarklet/js/$', "pins.views.bookmarklet_views.bookmarklet_js", name="bookmarklet_js"),
    url(r'^bookmarklet/pin/$', "pins.views.bookmarklet_views.pin_bookmarklet", name="pin_bookmarklet"),
    url(r'^bookmarklet/own/$', "pins.views.bookmarklet_views.own_bookmarklet", name="own_bookmarklet"),
    url(r'^bookmarklet/want/$', "pins.views.bookmarklet_views.want_bookmarklet", name="want_bookmarklet"),
    url(r'^bookmarklet/finished/(?P<pin_pk>\d+)/$', "pins.views.bookmarklet_views.bookmarklet_finished", name="bookmarklet_finished"),
    url(r'^bookmarklet/finish/$', "pins.views.finish_web_pin", name="finish_bookmarklet_pin", kwargs={'success_urlname':'bookmarklet_finished', 'pin_source': 'bookmarklet'}),
    url(r'^bookmarklet/finishown/$', "pins.views.finish_web_owant", name="finish_bookmarklet_own", kwargs={'success_urlname':'bookmarklet_finished', 'pin_source': 'bookmarklet', 'owant_type': 'own'}),
    url(r'^bookmarklet/finishwant/$', "pins.views.finish_web_owant", name="finish_bookmarklet_want", kwargs={'success_urlname':'bookmarklet_finished', 'pin_source': 'bookmarklet', 'owant_type': 'want'}),
)
#bookmarklet urls
urlpatterns = urlpatterns + patterns('',
    url(r'^button/js/$', "pins.views.button_views.button_js", name="button_js"),
    url(r'^button/iframe/$', "pins.views.button_views.button_iframe", name="button_iframe"),
    url(r'^button/pin/$', "pins.views.button_views.pin_button", name="pin_button"),
    url(r'^button/finished/(?P<pin_pk>\d+)/$', "pins.views.bookmarklet_views.bookmarklet_finished", name="button_finished"),
    url(r'^button/finish/$', "pins.views.finish_web_pin", name="finish_button_pin", kwargs={'success_urlname':'button_finished', 'pin_source': 'button'}),
)

#category urls
urlpatterns = urlpatterns + patterns('',
    url(r'^category/(?P<pk>\d+)/(?P<slug>[\w\d-]+)/$', "pins.views.single_category", 
            name="single_category"),
)

