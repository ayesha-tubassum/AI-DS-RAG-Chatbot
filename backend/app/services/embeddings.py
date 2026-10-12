"""
Embedding service using the Google Gen AI Python SDK (google-genai).

Verified against official Google Gemini API embedding docs (last checked Oct 2026):
  https://ai.google.dev/gemini-api/docs/embeddings

Model: gemini-embedding-001 (stable, GA April 2026 — text-only; correct for RAG).
Dimension: 3072 by default (configurable via EMBEDDING_DIMENSION to 768/1536/3072).

Key SDK facts baked into this implementation:
  - client.aio.models.embed_content(model, contents, config=EmbedContentConfig(...))
  - contents accepts a str (single) or list[str] (batch) in a single call.
  - EmbedContentConfig(task_type=..., output_dimensionality=...)
    task_type: RETRIEVAL_QUERY  → user question at search time
               RETRIEVAL_DOCUMENT → book passage at index time
  - output_dimensionality: any int 128–3072; recommended 768 / 1536 / 3072.
  - Normalization:
      * 3072-dim: API always returns L2-normalized vectors → no manual step.
      * 768/1536-dim on gemini-embedding-001: API does NOT normalize → must
        normalize manually before storing/comparing (Gemini Embedding 2 does
        auto-normalize, but gemini-embedding-001 does not).
  - Rate limits (free tier): ~100 RPM, 1500 RPD.  We retry on 429 / 5xx.
  - Batch size: single embed_content call; Google recommends ≤ 100 texts.
    We split into BATCH_SIZE chunks so large ingestion jobs don't OOM.
"""

from __future__ import annotations

import asyncio
import logging
import math
from typing import Sequence

from google import genai
from google.genai import types
from google.genai.errors import APIError as GeminiAPIError

from app.config import get_settings
from app.core.errors import EmbeddingError, NotConfiguredError

logger = logging.getLogger(__name__)

# Maximum texts per single embed_content call.
# Google's own examples use up to 100; we stay well within that.
BATCH_SIZE = 50

# Retry configuration for transient errors (429 rate-limit, 5xx server errors).
# Delays (seconds): 2, 4, 8 — enough to ride out a short burst.
_RETRY_DELAYS = (2.0, 4.0, 8.0)
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


# ---------------------------------------------------------------------------
# Client factory — injectable for tests
# ---------------------------------------------------------------------------

def _make_client(api_key: str) -> genai.Client:
    """Create and return a google-genai async-capable client."""
    return genai.Client(api_key=api_key)


def _get_client() -> genai.Client:
    """
    Return an authenticated Gemini client.

    Raises:
        NotConfiguredError: If GOOGLE_API_KEY is absent from settings.
    """
    settings = get_settings()
    if not settings.google_configured:
        raise NotConfiguredError("Gemini embeddings", ["GOOGLE_API_KEY"])
    # api_key is never logged; _make_client is separated so tests can patch it.
    return _make_client(settings.google_api_key)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Normalization helper
# ---------------------------------------------------------------------------

def _maybe_normalize(vector: list[float], dimension: int) -> list[float]:
    """
    L2-normalize ``vector`` if the model + dimension require it.

    gemini-embedding-001 returns already-normalized vectors at 3072 dims.
    At reduced dimensions (768, 1536) it does NOT normalize — we must do it
    so cosine similarity works correctly in Qdrant.

    Reference: https://ai.google.dev/gemini-api/docs/embeddings
    "Older Models: If you are using gemini-embedding-001, you must manually
     normalize non-3072 dimensions."
    """
    if dimension == 3072:
        return vector  # already normalized by the API

    # Compute L2 norm
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        logger.warning("Embedding vector has zero norm; skipping normalization.")
        return vector
    return [x / norm for x in vector]


# ---------------------------------------------------------------------------
# Internal retry wrapper
# ---------------------------------------------------------------------------

async def _embed_with_retry(
    client: genai.Client,
    model: str,
    contents: str | list[str],
    config: types.EmbedContentConfig,
) -> types.EmbedContentResponse:
    """
    Call embed_content with exponential back-off on transient errors.

    Raises:
        EmbeddingError: After all retries are exhausted, or on a non-retryable
                        error.  The error message never contains the API key.
    """
    last_exc: Exception | None = None

    for attempt, delay in enumerate((*_RETRY_DELAYS, None), start=1):
        try:
            return await client.aio.models.embed_content(
                model=model,
                contents=contents,
                config=config,
            )
        except GeminiAPIError as exc:
            status = getattr(exc, "code", None)
            if status in _RETRYABLE_STATUS_CODES and delay is not None:
                logger.warning(
                    "Embedding attempt %d failed (status=%s); retrying in %.0fs",
                    attempt,
                    status,
                    delay,
                )
                await asyncio.sleep(delay)
                last_exc = exc
                continue
            # Non-retryable Gemini API error
            raise EmbeddingError(f"Gemini API error (status={status}): {type(exc).__name__}") from exc
        except Exception as exc:
            # Any other unexpected error — don't retry, surface immediately.
            raise EmbeddingError(f"Unexpected error during embedding: {type(exc).__name__}") from exc

    # All retries exhausted
    raise EmbeddingError(
        f"Embedding failed after {len(_RETRY_DELAYS) + 1} attempts."
    ) from last_exc


# ---------------------------------------------------------------------------
# Internal single-chunk embed
# ---------------------------------------------------------------------------

async def _embed_chunk(
    client: genai.Client,
    texts: list[str],
    task_type: str,
    model: str,
    dimension: int,
) -> list[list[float]]:
    """Embed one batch of texts (len ≤ BATCH_SIZE) and normalize if needed."""
    config = types.EmbedContentConfig(
        task_type=task_type,
        output_dimensionality=dimension,
    )

    response = await _embed_with_retry(
        client=client,
        model=model,
        contents=texts,
        config=config,
    )

    if not response.embeddings or len(response.embeddings) != len(texts):
        raise EmbeddingError(
            f"Expected {len(texts)} embeddings, "
            f"got {len(response.embeddings) if response.embeddings else 0}."
        )

    vectors: list[list[float]] = []
    for emb in response.embeddings:
        if not emb.values:
            raise EmbeddingError("API returned an empty embedding vector.")
        vec = list(emb.values)
        if len(vec) != dimension:
            raise EmbeddingError(
                f"Vector length mismatch: expected {dimension}, got {len(vec)}. "
                "Check EMBEDDING_DIMENSION matches the model's output."
            )
        vectors.append(_maybe_normalize(vec, dimension))

    return vectors


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def embed_query(
    text: str,
    *,
    client: genai.Client | None = None,
) -> list[float]:
    """
    Embed a single user question for retrieval (RETRIEVAL_QUERY task type).

    Args:
        text:   The user's question text.
        client: Optional pre-built client; pass one in tests to avoid
                real API calls.

    Returns:
        A list of floats of length ``settings.embedding_dimension``,
        L2-normalized.

    Raises:
        NotConfiguredError: GOOGLE_API_KEY is not set.
        EmbeddingError:     API call failed or returned unexpected output.
    """
    settings = get_settings()
    resolved_client = client or _get_client()

    results = await _embed_chunk(
        client=resolved_client,
        texts=[text],
        task_type="RETRIEVAL_QUERY",
        model=settings.embedding_model,
        dimension=settings.embedding_dimension,
    )
    return results[0]


async def embed_documents(
    texts: Sequence[str],
    *,
    client: genai.Client | None = None,
) -> list[list[float]]:
    """
    Embed a list of document passages for indexing (RETRIEVAL_DOCUMENT task type).

    Large lists are automatically split into chunks of ``BATCH_SIZE`` to stay
    within API limits.  Each chunk is awaited sequentially (simple, safe on the
    free tier).

    Args:
        texts:  Passage strings to embed.
        client: Optional pre-built client for testing.

    Returns:
        A list of float vectors in the same order as ``texts``, each of length
        ``settings.embedding_dimension``, L2-normalized.

    Raises:
        NotConfiguredError: GOOGLE_API_KEY is not set.
        EmbeddingError:     API call failed or returned unexpected output.
    """
    if not texts:
        return []

    settings = get_settings()
    resolved_client = client or _get_client()

    all_vectors: list[list[float]] = []
    text_list = list(texts)

    for i in range(0, len(text_list), BATCH_SIZE):
        chunk = text_list[i : i + BATCH_SIZE]
        logger.debug(
            "Embedding documents chunk %d/%d (%d texts)",
            i // BATCH_SIZE + 1,
            math.ceil(len(text_list) / BATCH_SIZE),
            len(chunk),
        )
        chunk_vectors = await _embed_chunk(
            client=resolved_client,
            texts=chunk,
            task_type="RETRIEVAL_DOCUMENT",
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
        all_vectors.extend(chunk_vectors)

    return all_vectors
