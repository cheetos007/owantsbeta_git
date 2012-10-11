from django.contrib import admin
from pins import models
from sorl.thumbnail.admin import AdminImageMixin
from modeltranslation.admin import TranslationAdmin

class CategoryAdmin(TranslationAdmin):
	list_display = ['name','is_active']
	readonly_fields = ['created_user', 'modified_user','created_datetime','modified_datetime']

admin.site.register(models.Category, CategoryAdmin)


class DefaultBoardAdmin(TranslationAdmin):
	list_display = ['name','is_active']
	readonly_fields = ['created_user', 'modified_user','created_datetime','modified_datetime']

admin.site.register(models.DefaultBoard, DefaultBoardAdmin)


class BoardAdmin(admin.ModelAdmin):
	list_display = ['name','category', 'user']
	readonly_fields = ['created_user', 'modified_user','created_datetime','modified_datetime']
	search_fields = ['name']

admin.site.register(models.Board, BoardAdmin)

class PinAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ['description','image','board','is_flagged', 'pin_source']
	list_display_links = list_display
	list_filter = ['is_flagged', 'pin_source']
	readonly_fields = ['domain', 'source_pin', 'repinned_pin', 'created_user', 'modified_user',
		'created_datetime','modified_datetime']
	search_fields = ['description','domain__domain_name']

	def queryset(self, request):
		return super(PinAdmin, self).queryset(request).select_related('board')

admin.site.register(models.Pin, PinAdmin)

class PinAdvertismentAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ['html_code', 'url','image', 'is_active','active_from','active_to','current_impressions',
		'max_impressions', 'created_user']
	list_display_links = list_display

	list_filter = ['is_active', ]
	readonly_fields = ['current_impressions', 'created_user','modified_user',
		'created_datetime','modified_datetime']

	search_fields = ['html_code','url']
	def queryset(self, request):
		return super(PinAdvertismentAdmin, self).queryset(request).select_related('created_user')

admin.site.register(models.PinAdvertisment, PinAdvertismentAdmin)