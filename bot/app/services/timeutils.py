"""Timezone helpers built on the stdlib zoneinfo (py3.12)."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def is_valid_timezone(tz: str) -> bool:
    try:
        ZoneInfo(tz)
        return True
    except (ZoneInfoNotFoundError, ValueError):
        return False


def now_in(tz: str) -> datetime:
    """Current local time in the given IANA timezone (tz-aware)."""
    return datetime.now(ZoneInfo(tz))


def local_naive_to_utc(naive: datetime, tz: str) -> datetime:
    """Interpret a naive local datetime as being in ``tz`` and return UTC."""
    aware = naive.replace(tzinfo=ZoneInfo(tz))
    return aware.astimezone(ZoneInfo("UTC"))


def utc_to_local(dt: datetime, tz: str) -> datetime:
    """Convert a (tz-aware, usually UTC) datetime into the user's timezone."""
    return dt.astimezone(ZoneInfo(tz))


def format_local(dt: datetime, tz: str) -> str:
    """Human-friendly local rendering, e.g. '2026-06-18 19:00'."""
    return utc_to_local(dt, tz).strftime("%Y-%m-%d %H:%M")
