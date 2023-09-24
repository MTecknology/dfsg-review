'''
DCheck Internationalization
'''
import locale
import logging
import os
import yaml


# Container for loaded translations
loaded_translations = {}

# Last loaded language
last_loaded = None


def load_translations(language, i18n_dir=None):
    '''
    Load translations for <language> from <i18n_dir>.
    '''
    if not i18n_dir:
        i18n_dir = os.path.join(
                os.path.dirname(os.path.abspath(__name__)),
                'dcheck', 'i18n')

    if not language:
        language = locale.getlocale()[0].partition('_')[0]

    translations_path = os.path.join(i18n_dir, f'{language}.yml')
    with open(translations_path, 'r', encoding='utf-8') as fh:
        logging.debug('Loading translations from %s.', translations_path)
        global loaded_translations
        global last_loaded
        loaded_translations[language] = yaml.load(fh, Loader=yaml.SafeLoader)
        last_loaded = language


def translate(key, language=None):
    '''
    Return translated text from a provided (text lookup) key.
    '''
    if not language:
        language = last_loaded
    if language not in loaded_translations:
        logging.critical('Translation %s requested but not loaded.', language)
    return loaded_translations[language].get(key, key)


# Convenient alias for translate()
t = translate
