def callable_setting(key):
	def inner_fn():
		from site_settings.helpers import get_setting
		return get_setting(key)
	return inner_fn


TWITTER_CONSUMER_KEY         = callable_setting('twitter_consumer_key') #tOAJ6mwxzxNgw0yh4pfhQA
TWITTER_CONSUMER_SECRET      = callable_setting('twitter_consumer_secret')#F2LxTHHBYHQ9a5tw8dj0K5ZJKuRpPJ1pEWhtDW5so
FACEBOOK_APP_ID              = '421963611180461' #callable_setting('facebook_app_id')	234777706620080
FACEBOOK_API_SECRET          = 'fb87b613ee0c2bd9d9d533e4d7593c29' #callable_setting('facebook_api_secret')	a991f3a9196169eaf247520a99efad9b
#LINKEDIN_CONSUMER_KEY        = ''
#LINKEDIN_CONSUMER_SECRET     = ''
#ORKUT_CONSUMER_KEY           = ''
#ORKUT_CONSUMER_SECRET        = ''
#GOOGLE_CONSUMER_KEY          = ''
#GOOGLE_CONSUMER_SECRET       = ''
GOOGLE_OAUTH2_CLIENT_ID      = callable_setting('google_oauth2_client_id')#'952623817784.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET  = callable_setting('google_oauth2_client_secret')#'ibHq3ISGmpn8fiTO4UnAdIWU'
#FOURSQUARE_CONSUMER_KEY      = ''
#FOURSQUARE_CONSUMER_SECRET   = ''


SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

SOCIAL_AUTH_DEFAULT_USERNAME = 'user'
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
SOCIAL_AUTH_CHANGE_SIGNAL_ONLY = False

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/welcome-wizard/"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'publish_stream', 'user_photos']

LOGIN_ERROR_URL = "/account/login_error/"


TEST_FACEBOOK_APP_ID = '234777706620080'
TEST_FACEBOOK_API_SECRET = 'a991f3a9196169eaf247520a99efad9b'