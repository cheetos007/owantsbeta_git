from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin

from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from pins.forms.button_forms import IframeParamsForm


class BookmarkletPlugin(CMSPluginBase):
    model = CMSPlugin
    name = _("Pin-it bookmarklet")
    render_template = "pins/cms/bookmarklet_plugin.html"
    text_enabled = True
    def render(self, context, instance, placeholder):
        return context

plugin_pool.register_plugin(BookmarkletPlugin)


class PinItButtonPlugin(CMSPluginBase):
    model = CMSPlugin
    name = _("Pin-it button")
    render_template = "pins/cms/pin_it_button_plugin.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        site = Site.objects.get_current()
        context['script_src'] = '//%s%s' % (site.domain, reverse('button_js'))
        context['iframe_src'] = 'http://%s%s' % (site.domain, reverse('button_iframe'))
        context['iframe_form'] = IframeParamsForm()
        return context
    class Media:
        js = ('js/pins/button_generator.js',)

plugin_pool.register_plugin(PinItButtonPlugin)