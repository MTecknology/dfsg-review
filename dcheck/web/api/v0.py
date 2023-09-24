'''
DCheck API v0 (Development Version)
Route Prefix: /v0/
'''
# Python
import bottle


@bottle.route('/v0/ping')
def v0_ping():
    return 'pong'
