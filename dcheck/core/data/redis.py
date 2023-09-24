'''
DCheck Data - Redis Backend
'''
# Python
import json
import redis

# DCheck
import dcheck.core.config


class DataEngine:
    '''
    Connect dcheck data to a redis backend.
    '''
    def __init__(self):
        self.connection = redis.StrictRedis.from_url(
                dcheck.core.config.get('redis_url'))

    def get(self, key):
        value = self.connection.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key, value):
        self.connection.set(key, json.dumps(value))

    def keys(self, pattern):
        return self.connection.keys(pattern)
