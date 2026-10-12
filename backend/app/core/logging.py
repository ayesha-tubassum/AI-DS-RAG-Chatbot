"""
Structured JSON logging configuration.

Call configure_logging() once at application startup (in main.py).
After that, use standard `logging.getLogger(__name__)` everywhere.

Rules enforced here:
- Log level is driven by the LOG_LEVEL env var (default INFO).
- Stack traces are logged server-side but never forwarded to API callers.
- Secret values (API keys, tokens) must NEVER be passed to any logger.
"""

import logging
import sys
from typing import Any

from app.config import get_settings


class _SafeJsonFormatter(logging.Formatter):
    """
    Minimal structured formatter that emits one JSON object per line.
    Uses only the stdlib so there is no extra dependency.
    """

    def format(self, record: logging.LogRecord) -> str:
        import json
        import traceback

        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            # Include the traceback text server-side; it will NOT be sent to
            # the client — the API layer returns only a generic error message.
            payload["exc"] = traceback.format_exception(*record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Set up the root logger.  Call once at startup."""
    settings = get_settings()
    level = getattr(logging, settings.log_level, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_SafeJsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
