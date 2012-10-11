"""Site settings for owants project. The site_settings is a django application which is designed to be re-usable.
    All settings are stored as attributes in py:class:`site_settings.models.Setting` model.
    If you need to add another setting, you have to add the required field in model, and add a field to admin definition of py:mod:`site_settings.admin`
    After that you need to run `./manage.py schemamigration site_settings --auto` to create migration and `./manage.py migrate site_settings` to execute the migration in database.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import trans_real

from audit_fields.models import BaseAuditModel

from modeltranslation.translator import translator, TranslationOptions

from sorl.thumbnail import ImageField

from site_settings import SITE_SETTINGS_CACHE_KEY, SITE_SETTINGS_CACHE_TIMEOUT
from site_settings.managers import SettingManager



class Setting(BaseAuditModel):
    """
    This table will contain quite a lot of columns, but it's easier to maintain because standard django admin will be used to edit settings.
    Also, some options need to be translateable, which would complicate these matters even more.
    To add a setting to site, simply add a field for this model and change this application's admin.py to reflect the new field.
    """
    is_active = models.BooleanField(verbose_name=_('is active'), default=True, 
            help_text=_("""This field can be used to store multiple sets of configurations.
                If this field is checked, the settings you edit will be used in site!"""))
    site_name = models.CharField(verbose_name=_('site name'), max_length=255, default="owants",
        help_text=_("Site name which will be used throughout the application."))

    administrator_email = models.EmailField(verbose_name=_("administrator's email"), max_length=255, default="admin@example.org", 
        help_text=_("Site administrator's e-mail address."))

    mailing_address = models.TextField(verbose_name=_('mailing address'), blank=True, help_text=_('Required if you need to comply with CAN-SPAM act.'))

    site_logo = ImageField(verbose_name=_("site logo"), upload_to="site_logos/", blank=True)


    watermark_enabled = models.BooleanField(verbose_name=_('watermark images'), default=False, help_text=_('Apply watermarks to images?'))
    watermark = ImageField(verbose_name=_('watermark'), upload_to='watermarks/', blank=True)
    watermark_position = models.CharField(max_length=10, verbose_name=_('watermark position'), default='south east', choices=
        (('north', _('North')), ('south', _('South')), ('west', _('West')), ('east', _('East')),
        ('north east', _('North east')), ('south east', _('South east')), ('north west', _('North west')),
        ('south west', _('South west')), ('center', _('Center'))))
    watermark_opacity = models.FloatField(verbose_name=_('watermark opacity'), default=0.3, help_text=_('Number from 0 to 1 where 0- opaque, 1- completely transparent watermark'))
    watermark_size = models.CharField(verbose_name=_('watermark size'), blank=True, max_length=9,
        help_text=_('This can either be a geometry string, as is usual with sorl-thumbnail ("x200", "200x200"), or a percentage. \
If given a percentage, the watermark will always be the given percentage of the thumbnail size.'))


    bookmarklet_title = models.CharField(verbose_name=_('bookmarklet_title'), max_length=50, default="owants", 
        help_text=_("This text will be shown in user's bookmarks after bookmarklet is installed"))

    #OAuth settings
    twitter_consumer_key = models.CharField(verbose_name=_('twitter consumer key'), max_length=60, 
        help_text=_("Twitter application's consumer key"), blank=True)
    twitter_consumer_secret = models.CharField(verbose_name=_('twitter consumer secret'), max_length=60, 
        help_text=_("Twitter application's consumer secret"), blank=True)
    facebook_app_id = models.CharField(verbose_name=_('facebook application id'), max_length=60, blank=True)
    facebook_api_secret = models.CharField(verbose_name=_('facebook application secret'), max_length=60, blank=True)
    google_oauth2_client_id = models.CharField(verbose_name=_('google OAuth2 client id'), max_length=60, blank=True)
    google_oauth2_client_secret = models.CharField(verbose_name=_('google OAuth2 client secret'), max_length=60, blank=True)


    #Social media settings
    twitter_handle = models.CharField(verbose_name=_('twitter handle'), max_length=100, blank=True, 
        help_text=_("If your site has a Twitter account, please fill it in here (without the @ symbol)"))
    allow_tweet = models.BooleanField(verbose_name=_('allow tweet'), default=True, 
        help_text=_("If this is enabled, users can share pins on Twitter."))
    allow_facebook_like = models.BooleanField(verbose_name=_('allow Facebook Like'), default=False, 
        help_text=_("If this is enabled, users can like pins on Facebook (you need to fill Facebook Application id & secret in OAuth section of settings"))

    google_analytics_tracking_id = models.CharField(max_length=20, verbose_name=_('Google Analytics tracking ID'),
        help_text=_('If you want to use Google Analytics, please fill in your tracking id here. Please note, that you only need to enter tracking ID, which looks like this: UA-58082344-1'),
        blank = True)



    objects = SettingManager()

    class Meta:
        verbose_name = _("setting")
        verbose_name_plural = _("settings")


class SettingTranslationOptions(TranslationOptions):
    """
    Translation options class for modeltranslation application.
    You should list fields for Setting module which need to be translated in the attribute `fields` of this class.
    """
    fields = ('site_name','bookmarklet_title')

translator.register(Setting, SettingTranslationOptions)

def update_cache(**kwargs):
    """
    Updates the cached settings information. Since the settings might be different to each language,
    we need to iterate over languages, activate the language, get translations for selected language, and update the data in cache.
    If kwargs['language'] is passed, settings for that language are returned.
    """

    for language in settings.LANGUAGES:
        language = language[0]
        setting_values = Setting.objects.get_language_settings(language)
        cache.set('%s_%s' % (SITE_SETTINGS_CACHE_KEY, language), setting_values, SITE_SETTINGS_CACHE_TIMEOUT)


models.signals.post_save.connect(update_cache, sender=Setting, dispatch_uid="site_settings.models")







