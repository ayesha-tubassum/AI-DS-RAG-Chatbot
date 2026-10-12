"""
Qdrant vector database service.

Uses AsyncQdrantClient (available since qdrant-client 1.6.1).

Payload schema stored per point:
    {
        "title":   str,   # chapter / page title
        "section": str,   # sub-section heading (empty string if none)
        "path":    str,   # Docusaurus URL path, e.g. "/module-01-python-foundations/variables-data-types"
        "text":    str,   # the raw passage text (used for context building)
    }
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
) -> list[ScoredPoint]:
    """
    Search the Qdrant collection for passages most similar to ``query_vector``.

    Args:
        query_vector: Embedding of the user's question.
        top_k: Maximum number of results to return.  Defaults to settings.rag_top_k.
        score_threshold: Minimum cosine similarity.  Defaults to settings.rag_score_threshold.

    Returns:
        A list of ScoredPoint objects, sorted by score descending.
        Each point's ``.payload`` contains title, section, path, and text.

    Raises:
        NotConfiguredError: If Qdrant is not configured.
        RetrievalError: If the search request fails.
    """
    settings = get_settings()
    top_k = top_k if top_k is not None else settings.rag_top_k
    score_threshold = score_threshold if score_threshold is not None else settings.rag_score_threshold

    client = _get_client()
    try:
        results = await client.query_points(
            collection_name=settings.qdrant_collection,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
        )
        return results.points
    except Exception as exc:
        logger.error("Qdrant search failed: %s", type(exc).__name__)
        raise RetrievalError(str(exc)) from exc
    finally:
        await client.close()


async def ensure_collection_exists() -> None:
    """
    Create the Qdrant collection if it does not already exist.

    This is called from ingestion scripts, not from the API path.
    Uses the embedding dimension from settings.

    Raises:
        NotConfiguredError: If Qdrant is not configured.
        RetrievalError: If the operation fails.
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
