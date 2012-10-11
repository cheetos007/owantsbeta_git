from django.contrib import admin

from profiles.models import Profile

class ProfileAdmin(admin.ModelAdmin):
	search_fields = ['user__username','user__first_name', 'user__last_name', 'about','location','website','user__email']
	list_display = ['user','location','last_ip']


admin.site.register(Profile, ProfileAdmin)