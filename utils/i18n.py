

import json
import os
from flask import session, request

_translations = {}
_fallback_lang = 'en'


def load_translations(app):
    trans_dir = os.path.join(app.root_path, 'translations')
    if not os.path.isdir(trans_dir):
        return
    for fname in os.listdir(trans_dir):
        if fname.endswith('.json'):
            lang = fname.rsplit('.', 1)[0]
            with open(os.path.join(trans_dir, fname), 'r', encoding='utf-8') as f:
                _translations[lang] = json.load(f)


def get_locale():
    lang = session.get('lang')
    if lang and lang in _translations:
        return lang
    lang = request.cookies.get('lang')
    if lang and lang in _translations:
        return lang
    return _fallback_lang


def translate(key, **kwargs):
    lang = get_locale()

    value = _translations.get(lang, {})
    for part in key.split('.'):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = None
            break

    if value is None:

        value = _translations.get(_fallback_lang, {})
        for part in key.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break

    if value is None:
        return key

    if kwargs:
        try:
            value = value.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return value


def init_i18n(app):
    load_translations(app)
    app.jinja_env.globals['_'] = translate
    app.jinja_env.globals['get_locale'] = get_locale
