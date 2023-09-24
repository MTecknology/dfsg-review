'''
DCheck Configuration
'''
import logging
import os
import yaml


# Default values
DEFAULT_CONFIGURATION = {
    'loglevel': 'INFO',
    'checklists': ['integrity'],
    'pending_dir': '/var/cache/dcheck/pending',
    'workspace_dir': '/var/cache/dcheck/extracted',
    'i18n_dir': None,
    'default_lang': 'en',
    'data_engine': 'redis',
    'redis_url': 'redis://127.0.0.1:6379/0',
    'sqlite_path': './dcheck-data.sqlite',
    'layout': {
        # Available Panels:
        #   AllChecklists, PackageChecklist, FileChecklist,
        #   FileList, FileContents, FileInfo, PersistentFiles
        'left': ['AllChecklists', 'FileList'],
        'center': ['FileContents', 'FileInfo'],
        'right': ['PersistentFiles'],
        },
    'images_dir': None,
    }

# Storage for loaded configuration
loaded_configuration = None


def load_configuration():
    '''
    Check for a config file in the current directory or /etc/dcheck/
    '''
    global loaded_configuration
    if loaded_configuration is None:
        loaded_configuration = DEFAULT_CONFIGURATION

    # Find best configuration file
    if os.environ.get('DCHECK_CONFIG'):
        config_path = os.environ['DCHECK_CONFIG']
    elif os.path.exists('./config.yml'):
        config_path = './config.yml'
    elif os.path.exists('/etc/dcheck/config.yml'):
        config_path = '/etc/dcheck/config.yml'
    else:
        logging.info('No configuration found; using defaults.')
        return False

    # Load values from selected configuration
    with open(config_path, 'r') as fh:
        logging.debug('Loading configuration from %s', config_path)
        config_values = yaml.safe_load(fh)
        if config_values:
            loaded_configuration.update(config_values)

    # Find images directory if not set
    if not loaded_configuration.get('images_dir'):
        loaded_configuration['images_dir'] = os.path.join(
                os.path.dirname(os.path.abspath(__name__)),
                'dcheck', 'images')


def get(key, default=None):
    '''
    Return a configuration value.
    '''
    return loaded_configuration.get(key, default)
