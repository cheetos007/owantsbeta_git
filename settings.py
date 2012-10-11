# -*- coding: utf-8 -*-
# Django settings for basic pinax project.

import os.path
import posixpath
import sys


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG


# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
    ("Kiran Polavarapu", "contact@tollynation.com"),
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'owantsbeta',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'owantspass',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "US/Pacific"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

gettext = lambda s: s
LANGUAGES = (
    ("en", gettext("English"))
)

SITE_ID = 1
SITE_NAME = 'owants.com'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
]

FILER_STATICMEDIA_PREFIX = STATIC_URL + "filer/"

STATICFILES_FINDERS = [
    "staticfiles.finders.FileSystemFinder",
    "staticfiles.finders.AppDirectoriesFinder",
    "staticfiles.finders.LegacyAppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Subdirectory of COMPRESS_ROOT to store the cached media files in
COMPRESS_OUTPUT_DIR = "cache"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "^s0epau5sz9s*a(^k*ozp2+45_nm%pfffnzi+s)@8ahq4ocz!z"


CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 1,
        },
    },
}


#redis connection information which stores followers/followees and other information related to who follows who
FOLLOW_REDIS_PARAMS = {
    'host': 'localhost',
    'port': 6379,
    #'unix_socket_path': '',
    #'password':'',
    'db': 2, # database number
    'test_db': 3, # redis database which is used for tests
}

#if enabled, profiling data will be written to redis database
PROFILE_ENABLED = False
#log only requests which take longer than PROFILE_MIN_TIME to generate
PROFILE_MIN_TIME = 0

PROFILING_REDIS_PARAMS = {
    'host': 'localhost',
    'port': 6379,
    #'unix_socket_path': '',
    #'password':'',
    'db': 4, # database number
}



ROOT_URLCONF = "urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "staticfiles.context_processors.static",
    
    "site_settings.context_processors.site_settings",
    
    "account.context_processors.account",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "pins.context_processors.pin_form_processor",
    "cms.context_processors.media",
    "sekizai.context_processors.sekizai",
    'social_auth.context_processors.social_auth_backends',

    
]

CMS_TEMPLATES = (
    ("cms/page.html", "Full size page"),
)

INSTALLED_APPS = [
    # theme goes first so that it"s possible to override other themes
    "themes.default",
   
    #admin tools goes before django admin because it overrides admin templates
     # Django
    "admin_tools",
    "admin_tools.theming",
    "admin_tools.menu",
    "admin_tools.dashboard",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.comments",
    "pinax.templatetags",
    

    
    # external
    "notification", # must be first
    "staticfiles",
    "compressor",
    "debug_toolbar",
    "mailer",
    "timezones",
    "emailconfirmation",
    "announcements",
    "pagination",
    "idios",
    "modeltranslation",
    "social_auth",
    
    # Pinax
    
    "pinax.apps.signup_codes",
    
    # project-dependencies
    "easy_thumbnails", #easy thumbnails is used by filer
    "sorl.thumbnail",
    "sorl_watermarker",
    "south",
    "cms",
    "mptt",
    "menus",
    "sekizai",
    "filer",
    

    "cms.plugins.text",
    "cms.plugins.twitter",
    "cms.plugins.googlemap",
    "cmsplugin_filer_file",
    "cmsplugin_filer_folder",
    "cmsplugin_filer_image",
    "cmsplugin_filer_teaser",
    "cmsplugin_filer_video",
    "haystack",

    "actstream",
]


MY_APPS = [
    # project
    "about",
    "profiles",
    "pins",
    "audit_fields",
    "comments",
    "site_settings",
    "abuse_reports",
    "profiling", 
    "invite_friends",
    "ip_ban",
    
    "django_extensions",
    #derived from pinax.apps.account
    "account",

    ]


INSTALLED_APPS.extend(MY_APPS)


COMMENTS_APP = "comments"

ACTSTREAM_ACTION_MODELS = ['auth.User','pins.Board', 'pins.Pin', 'comments.Comment', 'pins.Like']

SOUTH_TESTS_MIGRATE = False # To disable migrations and use syncdb instead
SKIP_SOUTH_TESTS = True # To disable South's own unit tests

THUMBNAIL_UPSCALE = False

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)


#whether to send e-mail when a new abuse report is submitted
SEND_EMAIL_FOR_ABUSE_REPORTS = True

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


EMAIL_BACKEND = "mailer.backend.DbBackend"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profile/user/%s/" % o.username,
}


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = True

AUTHENTICATION_BACKENDS = [
    "account.auth_backends.AuthenticationBackend",
    "social_auth.backends.twitter.TwitterBackend",
    "social_auth.backends.facebook.FacebookBackend",
    "social_auth.backends.google.GoogleOAuth2Backend"

]

LOGIN_URL = "/account/login/" # @@@ any way this can be a url name?
LOGIN_REDIRECT_URLNAME = "home"
LOGOUT_REDIRECT_URLNAME = "home"

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

ADMIN_TOOLS_MENU = 'apps.admintools_menu.menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'apps.admintools_menu.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'apps.admintools_menu.dashboard.CustomAppIndexDashboard'

MODELTRANSLATION_TRANSLATION_REGISTRY = "translation"
# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass

from social_auth_settings import *
from watermark_settings import *

SIGNUP_REDIRECT_URLNAME = 'welcome_wizard'

#setting variable which can be used to determine if system is running, or tests are run
#at the moment it's used for connection to redis- one database for tests, other for real database
#now it's also used for Facebook Graph API tests
#also, cache key prefix is set if running tests
if len(sys.argv)>1:
    INSIDE_TESTING = sys.argv[1:2][0] in ['test']
else:
    INSIDE_TESTING = False

if INSIDE_TESTING:
    CACHES['default']['KEY_PREFIX'] = 'test_'
    SERVE_MEDIA = True

SEKIZAI_IGNORE_VALIDATION = True
CMS_HIDE_UNTRANSLATED = False

AFFILIATE_LINKS_PROCESSOR = 'pins.affiliate_link_processors.simple_processor'

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
  #  "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "account.middleware.LocaleMiddleware",
    "pagination.middleware.PaginationMiddleware",
    "pinax.middleware.security.HideSensistiveFieldsMiddleware",
    "audit_fields.middleware.CurrentUserMiddleware",
    "middleware.LanguageChooserMiddleware",
    "middleware.IPBanMiddleware",
    "cms.middleware.multilingual.MultilingualURLMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
]

if DEBUG:
    MIDDLEWARE_CLASSES.append("debug_toolbar.middleware.DebugToolbarMiddleware")

if PROFILE_ENABLED:
    MIDDLEWARE_CLASSES.insert(0, "profiling.middleware.ProfilingMiddleware")


TEST_RUNNER = 'django_selenium.selenium_runner.SeleniumTestRunner'
EMAIL_HOST = "mail.tollynation.com"
EMAIL_PORT = 25
SERVER_EMAIL = "admin@tollynation.com"
