"""Reminder extraction via Groq LLM (llama-3.3-70b-versatile).

Turns free-form text (in any language) into a structured reminder:
    {title, datetime (local ISO), needs_clarification, reply_language, message}

The user's *current local time* and *timezone* are injected into the prompt so
relative expressions ("tomorrow", "завтра", "in an hour", "morgen", "mañana")
resolve correctly. The model answers in the same language the user used.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime

from app.config import settings
from app.services.groq_client import client as _client
from app.services.timeutils import local_naive_to_utc, now_in

logger = logging.getLogger(__name__)


@dataclass
class Extraction:
    title: str | None
    remind_at_utc: datetime | None  # None when time is missing/unclear
    needs_clarification: bool
    reply_language: str | None  # ISO code detected by the model, best-effort
    message: str | None  # model's clarifying question, in the user's language


_SYSTEM_PROMPT = """You are a reminder-parsing engine for a Telegram bot.
The user speaks in ANY language (ru, uk, en, de, es, fr, pl, it, ...). You must:
1. Detect what they want to be reminded about (the task/title).
2. Resolve WHEN the reminder should fire as an absolute local datetime.

You are given the user's CURRENT LOCAL TIME and TIMEZONE. Use them to resolve
relative expressions like "tomorrow", "завтра", "in an hour", "за годину",
"morgen", "in einer Stunde", "mañana", "demain", "jutro", "next friday", etc.

Reply with a SINGLE JSON object, no markdown, with exactly these keys:
{
  "title": string | null,            // the task, in the user's language; null if none
  "datetime": string | null,         // local time as "YYYY-MM-DDTHH:MM"; null if unknown/ambiguous
  "needs_clarification": boolean,     // true if time or task is missing/ambiguous
  "reply_language": string,          // ISO 639-1 code of the user's language
  "message": string | null           // a short clarifying question in the user's language, only if needs_clarification
}

Rules:
- "title" is the TASK itself, phrased concisely as an action to do — use the
  infinitive/dictionary form of the verb, NOT the grammatical form the speaker
  used about themselves. Examples:
    "напомни чтобы я посмотрела бота" -> title "посмотреть бота"
    "remind me I called mom"          -> title "call mom"
    "erinnere mich dass ich Brot kaufe" -> title "Brot kaufen"
  Keep it in the user's language. Drop filler like "напомни/remind me".
- "datetime" must be LOCAL wall-clock time in the user's timezone (no offset, no Z).
- If the user gives a time without a date, assume the soonest future occurrence.
- If no time can be determined, set datetime=null and needs_clarification=true,
  and put a short, friendly clarifying question in "message" (user's language).
- Never invent a time. Prefer asking over guessing.
- Output ONLY the JSON object."""


async def extract(text: str, *, tz: str) -> Extraction:
    """Extract a structured reminder from free-form text."""
    now_local = now_in(tz)
    user_ctx = (
        f"Current local time: {now_local.strftime('%Y-%m-%dT%H:%M')} "
        f"({now_local.strftime('%A')}). Timezone: {tz}.\n\n"
        f"User message:\n{text}"
    )

    completion = await _client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_ctx},
        ],
    )
    raw = completion.choices[0].message.content or "{}"

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("LLM returned non-JSON: %r", raw)
        return Extraction(None, None, True, None, None)

    from app.constants import capitalize_first

    title = capitalize_first((data.get("title") or "").strip()) or None
    dt_local_str = data.get("datetime")
    needs = bool(data.get("needs_clarification", False))
    reply_language = data.get("reply_language")
    message = (data.get("message") or "").strip() or None

    remind_at_utc: datetime | None = None
    if dt_local_str:
        try:
            naive = datetime.fromisoformat(dt_local_str)
            naive = naive.replace(tzinfo=None)  # ensure naive before localizing
            remind_at_utc = local_naive_to_utc(naive, tz)
        except (ValueError, TypeError):
            logger.warning("Bad datetime from LLM: %r", dt_local_str)
            needs = True

    # Treat a missing title or time as needing clarification.
    if title is None or remind_at_utc is None:
        needs = True

    return Extraction(
        title=title,
        remind_at_utc=remind_at_utc,
        needs_clarification=needs,
        reply_language=reply_language,
        message=message,
    )
