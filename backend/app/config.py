"""
Application configuration loaded from environment variables / .env file.

All secrets are accessed only through this module; they are never logged.
Missing secrets do NOT crash the application at startup — they produce a
clear NotConfiguredError only when the feature that requires them is called.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Extra fields in .env are silently ignored
        extra="ignore",
    )

    # ── Google / Gemini ──────────────────────────────────────────────────
    # Required for embedding and generation; left optional here so /health
    # can report "not configured" instead of crashing on startup.
    google_api_key: str | None = Field(default=None)

    # gemini-embedding-001 is the current GA embedding model (July 2025).
    # Default dimension 3072 matches its native output (MRL-capable).
    embedding_model: str = Field(default="gemini-embedding-001")
    embedding_dimension: int = Field(default=3072)

    # gemini-2.0-flash is the current standard fast-generation model.
    generation_model: str = Field(default="gemini-2.0-flash")

    # ── Qdrant ──────────────────────────────────────────────────────────
    qdrant_url: str | None = Field(default=None)
    qdrant_api_key: str | None = Field(default=None)
    qdrant_collection: str = Field(default="ai_ds_book")

    # ── RAG behaviour ───────────────────────────────────────────────────
    rag_top_k: int = Field(default=5, ge=1, le=20)
    # Minimum cosine similarity score [0, 1] for a chunk to be used as
    # evidence.  Below this threshold the refusal message is returned
    # without calling the generation model.
    rag_score_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    # ── Server / CORS ────────────────────────────────────────────────────
    # Comma-separated list of allowed origins.
    # Example: "http://localhost:3000,https://my-book.vercel.app"
    allowed_origins: str = Field(default="http://localhost:3000")

    environment: Literal["development", "production"] = Field(default="development")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    # ── Derived helpers (not logged) ─────────────────────────────────────

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse the comma-separated origins string into a list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def google_configured(self) -> bool:
        return bool(self.google_api_key)

    @property
    def qdrant_configured(self) -> bool:
        return bool(self.qdrant_url and self.qdrant_api_key)

    @field_validator("embedding_dimension")
    @classmethod
    def validate_embedding_dimension(cls, v: int) -> int:
        allowed = {768, 1536, 3072}
        if v not in allowed:
            raise ValueError(
                f"embedding_dimension must be one of {allowed}; got {v}. "
                "See Matryoshka Representation Learning note in Google docs."
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached singleton settings instance."""
    return Settings()
