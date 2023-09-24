'''
DCheck Data
'''
# Python
import importlib

# DCheck
import dcheck.core.config

# Keep track of loaded engine
loaded_engine = None


def connect_storage():
    '''
    Load configured engine.
    '''
    global loaded_engine
    loaded_engine = importlib.import_module(
            '.' + dcheck.core.config.get('data_engine'),
            __name__).DataEngine()
    if not loaded_engine:
        raise Exception('Could not connect to the data engine.')


def __getattr__(name):
    '''
    Provide access to the engine functions.
    '''
    return getattr(loaded_engine, name)
