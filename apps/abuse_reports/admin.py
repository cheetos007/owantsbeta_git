from django.contrib import admin

from abuse_reports import models

class ReasonAdmin(admin.ModelAdmin):
	readonly_fields = ('created_user','modified_user','created_datetime','modified_datetime')

admin.site.register(models.AbuseReportReason, ReasonAdmin)


class ReportAdmin(admin.ModelAdmin):
	readonly_fields = ('reason', 'description', 'created_user','modified_user','created_datetime','modified_datetime', )
	list_display = ['description','status','created_datetime']
	list_filter = ('status',)


admin.site.register(models.AbuseReport, ReportAdmin)

