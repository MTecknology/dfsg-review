'''
Bootstrap Utilities
'''
# Python
import logging

# DCheck
import dcheck.core.config
import dcheck.core.data
import dcheck.checks
import dcheck.i18n


def start():
    '''
    Common setup for all entry points.
    '''
    # 1. Must load configuration first
    dcheck.core.config.load_configuration()

    # 2a. Configure translations
    log = logging.getLogger()
    log_level = getattr(logging, dcheck.core.config.get('loglevel'), 'INFO')
    log.setLevel(log_level)
    log_format = logging.Formatter('%(levelname)s:%(message)s')
    for h in log.handlers:
        h.setFormatter(log_format)

    # 2b. Configure translations
    dcheck.i18n.load_translations(
        language=dcheck.core.config.get('default_lang'),
        i18n_dir=dcheck.core.config.get('i18n_dir'))

    # 3. Remaining initialization
    dcheck.core.data.connect_storage()
    dcheck.checks.load_checklists()
