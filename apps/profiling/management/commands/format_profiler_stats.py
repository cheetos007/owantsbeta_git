from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from profiling.helpers import get_connection

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--clear-stats',
            action='store_true',
            dest='clear_stats',
            help='Clear profiler stats after output?'),
        )

    def handle(self, *args, **options):
        client = get_connection()
        rids = client.smembers('request_ids')
        pipe = client.pipeline(transaction=False)
        for rid in rids:
            pipe.hgetall('request:%s' % rid)

        results = pipe.execute()
        self.stdout.write('Request path, User id, Middleware queries, Middleware queries time (ms), View queries, View queries time (ms), Request total time (ms)\n')
        for r in results:
            self.stdout.write('%(path)s, %(user_id)s, %(middleware_queries)s, %(middleware_queries_time)s, %(view_queries)s, %(view_queries_time)s, %(total_time)s\n' % r)
            
        if options['clear_stats'] and len(rids)>0:
            client.srem('request_ids', *list(rids))














