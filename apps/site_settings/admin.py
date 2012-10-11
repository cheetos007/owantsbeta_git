from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from modeltranslation.admin import TranslationAdmin
from sorl.thumbnail.admin import AdminImageMixin


from site_settings.models import Setting
from site_settings.forms import SettingForm


class SettingAdmin(AdminImageMixin, TranslationAdmin):
	list_display = ['site_name','is_active', 'modified_user', 'modified_datetime']
	list_display_links = list_display
	list_filter = ['is_active']
	readonly_fields = ['created_user','modified_user','created_datetime', 'modified_datetime']
	form = SettingForm
	fieldsets = (
		(None, {
			'fields': ('site_name', 'site_logo','administrator_email','bookmarklet_title','mailing_address')
			}),
		(_('Analytics settings'), {
			'classes': ('collapse',),
			'fields': ('google_analytics_tracking_id',)
			}),
		(_('Social media settings'), {
			'classes': ('collapse',),
			'fields': ('twitter_handle', 'allow_tweet','allow_facebook_like',)
			}),
		(_('OAuth settings'), {
			'classes': ('collapse',),
			'fields': ('twitter_consumer_key', 'twitter_consumer_secret','facebook_app_id','facebook_api_secret', 
				'google_oauth2_client_id','google_oauth2_client_secret')
			}),
		(_('Watermark settings'), {
			'classes': ('collapse',),
			'fields': ('watermark_enabled', 'watermark','watermark_position','watermark_opacity', 
				'watermark_size')
			}),
		(_('Audit information'), {
			'classes': ('collapse',),
			'fields': ('is_active', 'created_user','modified_user','created_datetime', 'modified_datetime')
			})
		)

	def has_add_permission(self, request):
		"""
		Prohibits adding a new row of settings if there is already an active group of settings.
		"""
		if Setting.objects.filter(is_active=True).count()>0:
			return False
		return True

	def has_delete_permission(self, request, obj=None):
		"""
		Disallows deleting the last active settings row.
		"""
		if not obj:
			return True
		else:
			if Setting.objects.filter(is_active=True).exclude(pk=obj.pk).count()==0:
				return False
			return True

admin.site.register(Setting, SettingAdmin)