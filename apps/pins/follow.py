import redis
import time
from copy import deepcopy
import collections

from redis.connection import UnixDomainSocketConnection, Connection

from django.conf import settings



class FollowConnectionPool(object):
    _connection_pool = None

    def get_connection_pool(self, host='127.0.0.1', port=6379, db=1,
        password=None,
        unix_socket_path=None):
        if self._connection_pool is None:
            connection_class = (
                unix_socket_path and UnixDomainSocketConnection or Connection
            )
            kwargs = {
                'db': db,
                'password': password,
                'connection_class': connection_class,
            }
            if unix_socket_path is None:
                kwargs.update({
                    'host': host,
                    'port': port,
                })
            else:
                kwargs['path'] = unix_socket_path
            self._connection_pool = redis.ConnectionPool(**kwargs)
        return self._connection_pool

pool = FollowConnectionPool()


class Follow(object):

    def __init__(self):
        self.params = deepcopy(settings.FOLLOW_REDIS_PARAMS)
        if settings.INSIDE_TESTING:
            self.params['db'] = self.params.pop('test_db')
        else:
            del self.params['test_db']

        self.connection_pool = pool.get_connection_pool(**self.params)
        self._client = redis.StrictRedis(connection_pool=self.connection_pool)

    def _followers_key(self, user):
        return 'user:%d:followers' % user

    def _following_key(self, user):
        return 'user:%d:following' % user

    def _unfollowing_boards_key(self, user):
        return 'user:%d:unfollowing_boards' % user

    def _following_boards_key(self, user):
        return 'user:%d:following_boards' % user


    def flushdb(self):
        return self._client.flushdb()


    def delete_user_follower(self, user, follower):
        """
        Deletes followers for followee. If `followers` is a list of followers, only those are deleted.
        Otherwise, all followers are deleted.
        """
        from pins.models import Board
        pipe = self._client.pipeline()
        pipe.lrem(self._followers_key(user), 0, follower)
        pipe.lrem(self._following_key(follower),0, user)
        user_boards = Board.objects.get_user_boards(user)
        for b in user_boards:
            self.remove_user_unfollowed_board(follower, b.pk, pipe)

        return pipe.execute()



    def add_user_follower(self, followee, follower):
        """
        Adds follower to followee if it does not already exist. Duplicates are handled internally.
        """
        pipe = self._client.pipeline()
        pipe.lpush(self._followers_key(followee), follower) 
        pipe.lpush(self._following_key(follower), followee)

        return pipe.execute()



    def get_user_followers(self, user, from_range=0, to_range=-1):
        """Returns a list of followers for certain user"""
        return [int(i) for i in self._client.lrange(self._followers_key(user), from_range, to_range)]

    def get_user_following(self, user, from_range=0, to_range=-1):
        """Returns a list of users which are followed by user."""
        return [int(i) for i in self._client.lrange(self._following_key(user), from_range, to_range)]

    def add_user_unfollowed_board(self, user, board, pipe=False):
        client = pipe or self._client
        return client.lpush(self._unfollowing_boards_key(user), board)

    def remove_user_unfollowed_board(self, user, board, pipe=False):
        client = pipe or self._client
        return client.lrem(self._unfollowing_boards_key(user), 0, board)

    def get_user_unfollowed_boards(self, user, from_range=0, to_range=-1):
        """Returns a list of boards user is not following to"""

        return [int(i) for i in self._client.lrange(self._unfollowing_boards_key(user), from_range, to_range)]

    def add_user_followed_board(self, user, board, pipe=False):
        client = pipe or self._client
        return client.lpush(self._following_boards_key(user), board)

    def remove_user_followed_board(self, user, board, pipe=False):
        client = pipe or self._client
        return client.lrem(self._following_boards_key(user), 0, board)

    def get_user_followed_boards(self, user, from_range=0, to_range=-1):
        """Returns a list of boards user is following to"""

        return [int(i) for i in self._client.lrange(self._following_boards_key(user), from_range, to_range)]

    def is_following_user(self, user, followee):
        """Return True if user is following followee (user->followee)."""
        return str(followee) in self._client.lrange(self._following_key(user), 0, -1)

    def is_unfollowing_board(self, user, board):
        return str(board) in self._client.lrange(self._unfollowing_boards_key(user), 0, -1)

    def is_following_board(self, user, board):
        return str(board) in self._client.lrange(self._following_boards_key(user), 0, -1)



follow = Follow()