"""
embed_cache.py — local JSON cache of (content_hash → vector).

Purpose: avoid re-embedding unchanged chunks on re-runs or after interruptions.
The cache file lives at backend/.cache/embeddings.json and is gitignored.

Keys are content_hash (sha256 hex strings).
Values are lists of floats (the embedding vector).

Thread/process safety: writes are atomic (write-then-replace).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_CACHE_PATH = Path(__file__).resolve().parent.parent.parent / ".cache" / "embeddings.json"


class EmbedCache:
    """Simple content-hash → vector cache backed by a JSON file."""

    def __init__(self, cache_path: Path = _DEFAULT_CACHE_PATH) -> None:
        self._path = cache_path
        self._data: dict[str, list[float]] = {}
        self._dirty = False
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.debug("Loaded %d cached embeddings from %s", len(self._data), self._path)
            except Exception as exc:
                logger.warning("Could not load embed cache (%s); starting fresh.", exc)
                self._data = {}
        else:
            self._data = {}

    def get(self, content_hash: str) -> list[float] | None:
        return self._data.get(content_hash)

    def set(self, content_hash: str, vector: list[float]) -> None:
        self._data[content_hash] = vector
        self._dirty = True

    def save(self) -> None:
        """Persist to disk atomically."""
        if not self._dirty:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f)
            # Atomic rename
            os.replace(tmp, self._path)
            self._dirty = False
            logger.debug("Saved %d embeddings to cache.", len(self._data))
        except Exception as exc:
            logger.warning("Failed to save embed cache: %s", exc)
            if tmp.exists():
                tmp.unlink(missing_ok=True)

    def __len__(self) -> int:
        return len(self._data)
