"""
FastAPI application factory.

This module:
  - Creates the FastAPI app instance
  - Configures CORS (no wildcard in production)
  - Registers API routers
  - Sets up structured logging on startup
  - Exposes `app` for uvicorn and for the Vercel adapter in api/index.py
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, health
from app.config import get_settings
from app.core.logging import configure_logging

# Configure logging as early as possible so startup messages are captured.
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    s = get_settings()
    logger.info(
        "Backend started | env=%s google=%s qdrant=%s",
        s.environment,
        s.google_configured,
        s.qdrant_configured,
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI & Data Science Book — RAG Chat API",
        description=(
            "Answers questions using only content from the "
            '"AI & Data Science: A Practical Learning Path" book.'
        ),
        version="0.1.0",
        lifespan=lifespan,
        # Hide /docs and /redoc in production to reduce attack surface.
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    origins = settings.allowed_origins_list

    # Hard rule: never use wildcard in production.
    if settings.environment == "production" and "*" in origins:
        logger.warning(
            "Wildcard CORS origin ('*') is not allowed in production; "
            "set ALLOWED_ORIGINS to specific origins."
        )
        origins = [o for o in origins if o != "*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # ── Routers ───────────────────────────────────────────────────────────
    app.include_router(health.router)           # GET /health
    app.include_router(chat.router, prefix="/api")  # POST /api/chat

    return app


app = create_app()
