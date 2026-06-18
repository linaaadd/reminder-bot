"""Application configuration loaded from environment / .env file."""
from __future__ import annotations

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- required secrets ---
    telegram_bot_token: str
    groq_api_key: str
    database_url: str
    webapp_url: str = ""

    # --- bundled FastAPI server ---
    api_host: str = "0.0.0.0"
    # Railway injects $PORT at runtime; prefer it, then API_PORT, then 8000.
    api_port: int = Field(
        default=8000,
        validation_alias=AliasChoices("PORT", "API_PORT"),
    )

    # --- defaults ---
    default_timezone: str = "Europe/Berlin"

    # Groq models (overridable via env if needed)
    whisper_model: str = "whisper-large-v3"
    llm_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("telegram_bot_token", "groq_api_key", "database_url")
    @classmethod
    def _strip_secret(cls, v: str) -> str:
        """Trim stray whitespace/newlines from secrets.

        A trailing space pasted into an env var (e.g. GROQ_API_KEY) produces an
        ``Authorization: Bearer <key> `` header that h11 rejects with
        ``LocalProtocolError: Illegal header value`` — which surfaces as a
        misleading ``APIConnectionError('Connection error.')``.
        """
        return (v or "").strip()

    @field_validator("webapp_url")
    @classmethod
    def _normalize_webapp_url(cls, v: str) -> str:
        """Ensure an https scheme and no trailing slash.

        Telegram only accepts https WebApp URLs; a bare host like
        ``foo.up.railway.app`` (no scheme) is rejected with a 400. We add the
        scheme so a small config mistake doesn't break startup.
        """
        v = (v or "").strip().rstrip("/")
        if not v:
            return ""
        if v.startswith("http://"):
            v = "https://" + v[len("http://"):]
        elif not v.startswith("https://"):
            v = "https://" + v
        return v

    @property
    def webapp_url_is_https(self) -> bool:
        return self.webapp_url.startswith("https://")

    @property
    def async_database_url(self) -> str:
        """Normalize common Postgres DSNs to the asyncpg driver.

        Railway/Heroku hand out ``postgres://`` or ``postgresql://`` URLs;
        SQLAlchemy async needs the ``postgresql+asyncpg://`` scheme.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]
        return url


settings = Settings()  # type: ignore[call-arg]
