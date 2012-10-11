from django.conf.urls.defaults import *
from django.conf import settings

#pin urls
urlpatterns = patterns('',
    url(r'^report/(?P<content_type>\d+)/(?P<object_id>\d+)/$', "abuse_reports.views.report_abuse", name="report_abuse"),
    url(r'^preview_email/$', "abuse_reports.views.preview_email"),
)