'''
DCheck Web Frontend
'''
# Python
import bottle

# DCheck
import dcheck.web.api.v0  # noqa:F401 (import routes)


@bottle.route('/')
def basic():
    '''
    test
    '''
    return 'hello world'


def run(*args, **kwargs):
    bottle.run(*args, **kwargs)
