"""Tiny i18n helper. All strings live in ``locales.py``.

Language is chosen from the user's Telegram ``language_code`` (or the language
detected from their message), falling back to English. Unknown keys/langs never
crash — they degrade to English, then to the raw key.
"""
from __future__ import annotations

from app.i18n.locales import LOCALES

FALLBACK = "en"
SUPPORTED = tuple(LOCALES.keys())


def normalize_lang(code: str | None) -> str:
    """Map a Telegram language_code ('de-DE', 'uk') to a supported locale."""
    if not code:
        return FALLBACK
    short = code.split("-")[0].lower()
    return short if short in LOCALES else FALLBACK


def t(key: str, lang: str | None = None, /, **kwargs: object) -> str:
    """Translate ``key`` into ``lang`` with ``str.format`` interpolation."""
    locale = normalize_lang(lang)
    table = LOCALES.get(locale, LOCALES[FALLBACK])
    template = table.get(key) or LOCALES[FALLBACK].get(key) or key
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
