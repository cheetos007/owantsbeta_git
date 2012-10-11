from site_settings.models import Setting

def get_setting(key, default=None):
	"""
	Returns setting from cache with a name of key.
	You can also pass default value which is returned when such setting is not found.
	"""
	settings = Setting.objects.get_settings()
	if settings:
		return settings.get(key, default)
	else:
		return default

