from django.conf import settings

from django.contrib.sites.models import Site
from site_settings.helpers import get_setting

def site_settings(request):
    ctx = {}
    
    if Site._meta.installed:
        site = Site.objects.get_current()
        ctx.update({
            "SITE_NAME": get_setting('site_name', site.name),
            "SITE_DOMAIN": site.domain
        })
    
    return ctx