import redis
from django.conf import settings

def get_connection():
	params = settings.PROFILING_REDIS_PARAMS
	return redis.StrictRedis(**params)
