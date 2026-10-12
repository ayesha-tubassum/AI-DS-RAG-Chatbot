"""
Embedding service using the Google Gen AI SDK (google-genai).

API reference:
  client.aio.models.embed_content(
      model=<str>,
      contents=<str | list[str]>,
      config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY" | "RETRIEVAL_DOCUMENT"),
  )
  Returns: EmbedContentResponse with .embeddings list[ContentEmbedding],
           each with .values: list[float]

task_type is important for gemini-embedding-001:
  - RETRIEVAL_DOCUMENT  → used when indexing book passages
  - RETRIEVAL_QUERY     → used when embedding a user question at query time
"""

import logging
from typing import Literal

from google import genai
from google.genai import types

from app.config import get_settings
from app.core.errors import EmbeddingError, NotConfiguredError

logger = logging.getLogger(__name__)

TaskType = Literal["RETRIEVAL_QUERY", "RETRIEVAL_DOCUMENT"]


def _get_client() -> genai.Client:
    """Return an authenticated Gemini client, raising NotConfiguredError if the key is absent."""
    settings = get_settings()
    if not settings.google_configured:
        raise NotConfiguredError("Gemini embeddings", ["GOOGLE_API_KEY"])
    # The client is lightweight; callers may cache it themselves if needed.
    return genai.Client(api_key=settings.google_api_key)


async def embed_text(text: str, task_type: TaskType = "RETRIEVAL_QUERY") -> list[float]:
    """
    Embed a single text string using the configured Gemini embedding model.

    Args:
        text: The text to embed (question or document passage).
        task_type: ``RETRIEVAL_QUERY`` for a user question;
                   ``RETRIEVAL_DOCUMENT`` for a book passage being indexed.

    Returns:
        A list of floats representing the embedding vector.

    Raises:
        NotConfiguredError: If GOOGLE_API_KEY is not set.
        EmbeddingError: If the API call fails.
    """
    settings = get_settings()
    client = _get_client()

    try:
        response = await client.aio.models.embed_content(
            model=settings.embedding_model,
            contents=text,
            config=types.EmbedContentConfig(task_type=task_type),
        )
    except Exception as exc:
        # Do not log the text itself in case it contains PII.
        logger.error("Embedding API call failed: %s", type(exc).__name__)
        raise EmbeddingError(str(exc)) from exc

    if not response.embeddings or not response.embeddings[0].values:
        raise EmbeddingError("API returned an empty embedding vector.")

    return list(response.embeddings[0].values)


async def embed_batch(
    texts: list[str], task_type: TaskType = "RETRIEVAL_DOCUMENT"
) -> list[list[float]]:
    """
    Embed multiple texts in a single API call.

    Args:
        texts: List of text strings to embed.
        task_type: Task type applied to all texts in the batch.

    Returns:
        A list of embedding vectors, in the same order as ``texts``.

    Raises:
        NotConfiguredError: If GOOGLE_API_KEY is not set.
        EmbeddingError: If the API call fails or the response is malformed.
    """
    settings = get_settings()
    client = _get_client()

    try:
        response = await client.aio.models.embed_content(
            model=settings.embedding_model,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type),
        )
    except Exception as exc:
        logger.error("Batch embedding API call failed: %s", type(exc).__name__)
        raise EmbeddingError(str(exc)) from exc

    if not response.embeddings or len(response.embeddings) != len(texts):
        raise EmbeddingError(
            f"Expected {len(texts)} embeddings, got "
            f"{len(response.embeddings) if response.embeddings else 0}."
        )

    return [list(e.values) for e in response.embeddings]
