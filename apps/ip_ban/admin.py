from django.contrib import admin
from ip_ban.models import BanIP

class BanIPAdmin(admin.ModelAdmin):
    list_display = ['ip_range', 'created_user','created_datetime','modified_user','modified_datetime']
    readonly_fields = ['created_user','created_datetime','modified_user','modified_datetime']
    
    
admin.site.register(BanIP, BanIPAdmin)