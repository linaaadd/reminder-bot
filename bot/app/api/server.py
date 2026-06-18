"""FastAPI app factory for the WebApp backend."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


def create_api() -> FastAPI:
    app = FastAPI(title="Reminder Bot API", version="1.0.0")

    # The WebApp is served from a different origin (Railway static / Vite dev),
    # so allow cross-origin calls. Auth is via signed initData, not cookies,
    # so a permissive CORS policy is safe here.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
