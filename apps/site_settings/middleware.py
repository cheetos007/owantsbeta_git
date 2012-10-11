"""
For efficiency reasons, settings are loaded from cache on each page load and stored in thread's local namespace.
"""
from threading import local
from site_settings.models import Setting

thread_namespace = local()

class SiteSettingMiddleware(object):
    def process_request(self, request):
        thread_namespace.site_settings = Setting.objects.get_settings()

    def process_response(self, request, response):
        thread_namespace.site_settings = None
        return response