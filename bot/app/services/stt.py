"""Speech-to-text via Groq Whisper (whisper-large-v3).

Telegram voice notes arrive as ``.oga`` (Opus audio in an OGG container).
Groq's transcription endpoint accepts OGG, so in the common case we send the
bytes as-is. As a safety net (some edge containers / future formats) we try to
transcode to MP3 with ffmpeg if it's available and the raw upload fails.

Language is NOT forced — whisper-large-v3 auto-detects it, which is required
for the multilingual behaviour the project needs (ru/uk/en/de/es/fr/pl/...).
"""
from __future__ import annotations

import asyncio
import logging
import shutil

from groq import AsyncGroq

from app.config import settings

logger = logging.getLogger(__name__)

_client = AsyncGroq(api_key=settings.groq_api_key)


async def _transcribe_bytes(data: bytes, filename: str) -> str:
    resp = await _client.audio.transcriptions.create(
        file=(filename, data),
        model=settings.whisper_model,
        # No `language=` — let Whisper auto-detect (multilingual requirement).
        response_format="text",
    )
    # With response_format="text" the SDK returns a plain string.
    return resp if isinstance(resp, str) else getattr(resp, "text", str(resp))


async def _ffmpeg_to_mp3(data: bytes) -> bytes | None:
    """Transcode arbitrary audio bytes to MP3 via ffmpeg. None if unavailable."""
    if shutil.which("ffmpeg") is None:
        return None
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-i", "pipe:0", "-f", "mp3", "-ac", "1", "-ar", "16000",
        "pipe:1",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    out, _ = await proc.communicate(input=data)
    if proc.returncode != 0 or not out:
        return None
    return out


async def transcribe(data: bytes, *, filename: str = "audio.ogg") -> str:
    """Transcribe audio bytes to text. Raises on unrecoverable failure."""
    try:
        text = await _transcribe_bytes(data, filename)
        return text.strip()
    except Exception as exc:  # noqa: BLE001 - we want a fallback path
        logger.warning("Whisper raw upload failed (%s); trying ffmpeg", exc)
        mp3 = await _ffmpeg_to_mp3(data)
        if mp3 is None:
            raise
        text = await _transcribe_bytes(mp3, "audio.mp3")
        return text.strip()
