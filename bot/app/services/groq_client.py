"""Shared Groq async client, pinned to IPv4.

Why force IPv4
--------------
On some hosts (notably Railway) outbound IPv6 to Groq/Cloudflare is broken or
unrouted, so the SDK's connection attempts fail with
``APIConnectionError('Connection error.')`` even though IPv4 egress works fine
(Telegram, which is IPv4-only, keeps working). Binding the httpx transport's
source address to ``0.0.0.0`` forces IPv4 and sidesteps the dead IPv6 path.

We pass our own ``http_client`` so the Groq SDK doesn't build its own (which
also avoids the httpx ``proxies`` incompatibility).
"""
from __future__ import annotations

import httpx
from groq import AsyncGroq

from app.config import settings

# local_address="0.0.0.0" → bind source to an IPv4 interface (IPv4 only).
_http_client = httpx.AsyncClient(
    transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0", retries=1),
    timeout=httpx.Timeout(60.0, connect=15.0),
)

client = AsyncGroq(api_key=settings.groq_api_key, http_client=_http_client)
