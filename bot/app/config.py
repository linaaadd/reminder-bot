"""Application configuration loaded from environment / .env file."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- required secrets ---
    telegram_bot_token: str
    groq_api_key: str
    database_url: str
    webapp_url: str = ""

    # --- bundled FastAPI server ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000

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
