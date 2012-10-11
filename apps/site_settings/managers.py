from django.db import models
from django.core.cache import cache
from django.utils import translation

from site_settings import SITE_SETTINGS_CACHE_KEY




class SettingManager(models.Manager):

    def get_settings(self, use_cache=True):
        """Returns dict of all cached settings for current language"""
        from site_settings.models import update_cache
        language = translation.get_language()
        if '-' in language:
            language = language.split('-')[0]
        elif '_' in language:
            language = language.split('_')[0]

        if use_cache:
            cached_settings = cache.get('%s_%s' % (SITE_SETTINGS_CACHE_KEY, language))
            if cached_settings:
                return cached_settings
            else:
                update_cache()
                return cache.get('%s_%s' % (SITE_SETTINGS_CACHE_KEY, language))
        else:
            return self.get_language_settings(language)

    def get_language_settings(self, language):
        setting_values = self.filter(is_active=True).values()

        if len(setting_values)>0:
            #since values() cannot provide automatic translation of fields by modeltranslation, we need to manually set keys to correct values
            setting_values = setting_values[0]        
            for item in setting_values.items():
                if "%s_%s" % (item[0], language) in setting_values:
                    setting_values[item[0]] = setting_values["%s_%s" % (item[0], language)]
            return setting_values
        else:
            return {}
