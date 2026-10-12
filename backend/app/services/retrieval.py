"""
Retrieval layer: combines embedding and vector search into one call.

This keeps rag_service.py clean — it only needs to call retrieve() and
then decide whether the results are good enough to send to generation.
"""

import logging

from app.config import get_settings
from app.core.errors import EmbeddingError, NotConfiguredError, RetrievalError
from app.schemas import Source
from app.services import embeddings as emb_service
from app.services import qdrant_service

logger = logging.getLogger(__name__)


async def retrieve(question: str) -> tuple[list[Source], list[str]]:
    """
    Embed ``question`` and search Qdrant for relevant book passages.

    Returns a tuple of:
        sources  – list of Source objects (metadata for the API response)
        passages – list of raw text strings (used to build the generation prompt)

    The score threshold filtering is applied inside qdrant_service.search_similar,
    so any result returned here already meets the minimum quality bar.

    Raises:
        NotConfiguredError: If Google or Qdrant are not configured.
        EmbeddingError: If embedding the question fails.
        RetrievalError: If the Qdrant search fails.
    """
    settings = get_settings()

    # Step 1: embed the question
    query_vector = await emb_service.embed_text(question, task_type="RETRIEVAL_QUERY")

    # Step 2: search Qdrant
    hits = await qdrant_service.search_similar(
        query_vector=query_vector,
        top_k=settings.rag_top_k,
        score_threshold=settings.rag_score_threshold,
    )

    if not hits:
        logger.info("No results above score threshold for question (length=%d)", len(question))
        return [], []

    sources: list[Source] = []
    passages: list[str] = []

    for hit in hits:
        payload = hit.payload or {}
        sources.append(
            Source(
                title=payload.get("title", ""),
                section=payload.get("section", ""),
                path=payload.get("path", ""),
                score=round(hit.score, 4),
            )
        )
        if text := payload.get("text", ""):
            passages.append(text)

    return sources, passages
