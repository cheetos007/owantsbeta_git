import os
import datetime
from django.db import connection
from django.conf import settings
from profiling.helpers import get_connection

def total_query_time():
	timesql=0.0
	for q in connection.queries:
		timesql+=float(q['time'])
	return timesql

class ProfilingMiddleware(object):

	def process_request(self, request):
		if not 'site_media' in request.path and not '__debug__' in request.path:
			self.record_data = True
			self.start_dt = datetime.datetime.now()
		else:
			self.record_data = False

		return None

	def process_view(self, request, callback, callback_args, callback_kwargs):
		if self.record_data:
			self.middleware_queries_count = len(connection.queries)
			self.middleware_queries_time = total_query_time()
		return None

	def process_response(self, request, response):
		if self.record_data:
			self.view_queries_count = len(connection.queries)-self.middleware_queries_count
			self.view_queries_time = total_query_time() - self.middleware_queries_time
			td = datetime.datetime.now()-self.start_dt
			self.total_time = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**3
			if self.total_time> settings.PROFILE_MIN_TIME:
				self._write_data(request)
		return response


	def _write_data(self, request):
		"""
		Write data to redis instance which is also used for cache.
		"""
		client = get_connection()
		rid = client.incr('request_count')
		if request.user.is_authenticated():
			uid = request.user.pk
		else:
			uid = 0
		data = {'middleware_queries': self.middleware_queries_count, 'middleware_queries_time': self.middleware_queries_time,
				'path': request.path, 'user_id': uid, 'view_queries_time': self.view_queries_time, 'view_queries': self.view_queries_count,'total_time': self.total_time}
		client.hmset('request:%d' % rid, data)
		client.sadd('request_ids', rid)
