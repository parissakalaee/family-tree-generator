import json
from importlib.resources import files

import arabic_reshaper
from bidi.algorithm import get_display

from family_tree.fonts import STAR

with files('family_tree').joinpath('data', 'translations.json').open(encoding='utf-8') as f:
    _T: dict[str, dict[str, dict[str, str]]] = json.load(f)


def t_name(key: str, lang: str) -> str:
    """Translate a person name; fall back to the key itself."""
    v = _T['names'].get(key, {}).get(lang, '')
    return v if v else key


def t_ui(key: str, lang: str) -> str:
    """Translate a UI string; fall back to English."""
    v = _T['ui'].get(key, {}).get(lang, '')
    return v if v else _T['ui'].get(key, {}).get('en', key)


def fa_text(text: str, lang: str) -> str:
    """Reshape + bidi so ReportLab renders Persian correctly. No-op for non-Persian."""
    if lang != 'fa' or not text:
        return text
    return get_display(arabic_reshaper.reshape(str(text)))


def star_suffix(lang: str) -> str:
    """'  |  * = ' (fa) or '  |  ★ = ' (en/nl) — used in page subtitles."""
    return '  |  %s = ' % STAR[lang]
