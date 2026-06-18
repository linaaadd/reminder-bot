"""Shared constants and string-enum validation helpers."""
from __future__ import annotations

# Reminder lifecycle status.
STATUS_PENDING = "pending"
STATUS_DONE = "done"
STATUS_CANCELLED = "cancelled"
STATUSES = frozenset({STATUS_PENDING, STATUS_DONE, STATUS_CANCELLED})

# How a reminder was created.
SOURCE_VOICE = "voice"
SOURCE_TEXT = "text"
SOURCE_MANUAL = "manual"
SOURCES = frozenset({SOURCE_VOICE, SOURCE_TEXT, SOURCE_MANUAL})


def validate_status(value: str) -> str:
    if value not in STATUSES:
        raise ValueError(f"invalid status: {value!r}")
    return value


def validate_source(value: str) -> str:
    if value not in SOURCES:
        raise ValueError(f"invalid source: {value!r}")
    return value


def capitalize_first(s: str) -> str:
    """Uppercase the first character, leave the rest untouched.

    Unlike ``str.capitalize()`` this does not lowercase the remainder, so
    acronyms and proper nouns ("посмотреть Бота") survive.
    """
    s = (s or "").strip()
    return s[:1].upper() + s[1:] if s else s
