"""
OneBase i18n — lightweight runtime translation layer.

Design:
  - Help text (Typer decorators, docstrings) stays in English — no import-time issues.
  - Runtime output (logger, Panel, Table) goes through _() for translation.
  - Default language is English; use --lang zh or ONEBASE_LANG=zh for Chinese.
"""

import os

_current_lang: str = "en"
_translations: dict = {}


def set_lang(lang: str) -> None:
    """Activate a language. Called once in the Typer callback before any subcommand runs."""
    global _current_lang, _translations
    lang = (lang or os.getenv("ONEBASE_LANG", "en")).lower().strip()
    _current_lang = lang

    if lang == "zh":
        from .locales.zh import messages

        _translations = messages
    else:
        _translations = {}


def _(msg: str) -> str:
    """Translate *msg* at runtime. English is the source language; non-en looks up the table."""
    if _current_lang == "en":
        return msg
    return _translations.get(msg, msg)
