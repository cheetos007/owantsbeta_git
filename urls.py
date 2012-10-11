from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf.urls.static import static
from django.contrib import admin
from pinax.apps.account.openid_consumer import PinaxConsumer

from haystack.views import SearchView
from haystack.query import RelatedSearchQuerySet


admin.autodiscover()

handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^", include("pins.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("account.urls")),
    url(r"^profile/", include("profiles.urls")),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url('^activity/', include('actstream.urls')),
    url(r'^abuse/', include('abuse_reports.urls')),
    url(r'^invite/', include('invite_friends.urls')),
    url(r'^auth/', include('social_auth.urls')),
    url(r'^cms/', include('cms.urls')),
)

urlpatterns = urlpatterns + patterns('haystack.views',
    url(r'^search/$', SearchView(searchqueryset=RelatedSearchQuerySet()), name='haystack_search'),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls"),),
        url(r'^site_media/media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
        url(r'^site_media/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    )