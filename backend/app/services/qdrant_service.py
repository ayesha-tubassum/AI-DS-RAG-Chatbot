"""
Qdrant vector database service.

Uses AsyncQdrantClient (qdrant-client 1.19.1).

Verified API:
  client.query_points(
      collection_name, query=list[float], limit, score_threshold, with_payload
  ) → QueryResponse with .points: list[ScoredPoint]
  ScoredPoint fields: id, score, payload (dict)

Payload schema per point (set at ingestion time):
    title, section, path, source_file, module, chunk_index, text, content_hash
"""

import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, ScoredPoint, VectorParams

from app.config import get_settings
from app.core.errors import NotConfiguredError, RetrievalError

logger = logging.getLogger(__name__)


def _get_client() -> AsyncQdrantClient:
    """Return an authenticated AsyncQdrantClient, raising NotConfiguredError if unconfigured."""
    settings = get_settings()
    if not settings.qdrant_configured:
        raise NotConfiguredError("Qdrant vector search", ["QDRANT_URL", "QDRANT_API_KEY"])
    return AsyncQdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )


async def search_similar(
    query_vector: list[float],
    top_k: int | None = None,
    score_threshold: float | None = None,
    *,
    client: AsyncQdrantClient | None = None,
) -> list[ScoredPoint]:
    """
    Search the Qdrant collection for passages most similar to ``query_vector``.

    Args:
        query_vector:    Embedding of the user's question (list of floats).
        top_k:           Maximum number of results to return.
                         Defaults to settings.rag_top_k.
        score_threshold: Minimum cosine similarity to include.
                         Defaults to settings.rag_score_threshold.
                         Pass ``0.0`` to return ALL candidates without filtering
                         (used by the evaluation script).
        client:          Optional pre-built client; inject in tests to avoid
                         real API calls.

    Returns:
        List of ScoredPoint objects sorted by score descending.
        Each point's ``.payload`` contains: title, section, path, source_file,
        module, chunk_index, text, content_hash.

    Raises:
        NotConfiguredError: Qdrant is not configured.
        RetrievalError:     Search request failed.
    """
    settings = get_settings()
    top_k = top_k if top_k is not None else settings.rag_top_k
    score_threshold = score_threshold if score_threshold is not None else settings.rag_score_threshold

    resolved_client = client or _get_client()
    close_client = client is None  # only close if we created it

    try:
        results = await resolved_client.query_points(
            collection_name=settings.qdrant_collection,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
        )
        return results.points
    except Exception as exc:
        logger.error("Qdrant query_points failed: %s", type(exc).__name__)
        raise RetrievalError(str(exc)) from exc
    finally:
        if close_client:
            await resolved_client.close()


async def ensure_collection_exists() -> None:
    """
    Create the Qdrant collection if it does not already exist.

    Called from ingestion scripts, not from the API path.

    Raises:
        NotConfiguredError: Qdrant is not configured.
        RetrievalError:     Operation failed.
    """
    settings = get_settings()
    client = _get_client()
    try:
        exists = await client.collection_exists(settings.qdrant_collection)
        if not exists:
            await client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection '%s'", settings.qdrant_collection)
        else:
            logger.info("Qdrant collection '%s' already exists", settings.qdrant_collection)
    except NotConfiguredError:
        raise
    except Exception as exc:
        raise RetrievalError(str(exc)) from exc
    finally:
        await client.close()
