"""
Retrieval service: validate question → embed → search Qdrant → filter → return.

Design:
  - Does NOT generate any answer. Stays separately testable.
  - Embedding and Qdrant clients are injectable for unit tests.
  - Score threshold filtering happens here (not inside qdrant_service) so the
    evaluation script can call retrieve_candidates() without a threshold and
    then apply its own cutoff.
  - Diagnostic logging: question length, candidate count, top score, kept count.
    Secret values (API keys) are never logged.
"""

from __future__ import annotations

import logging
import re

from qdrant_client import AsyncQdrantClient
from google import genai

from app.config import get_settings
from app.core.errors import EmbeddingError, NotConfiguredError, RetrievalError
from app.schemas import Source
from app.services import embeddings as emb_service
from app.services import qdrant_service

logger = logging.getLogger(__name__)

# ── Question validation constants ─────────────────────────────────────────────
QUESTION_MIN_LEN = 1
QUESTION_MAX_LEN = 1000
_COLLAPSE_WHITESPACE = re.compile(r"\s+")


# ── Public result type ────────────────────────────────────────────────────────

class RetrievalResult:
    """
    Outcome of a retrieval call.

    Attributes:
        sources:  Metadata for each kept chunk (used in the API response).
        passages: Raw text for each kept chunk (used to build the RAG prompt).
        top_score: Score of the highest-ranked result (0.0 if no candidates).
        all_candidates_count: Total candidates returned by Qdrant before threshold.
        kept_count: Number of results that passed the score threshold.
    """

    __slots__ = ("sources", "passages", "top_score", "all_candidates_count", "kept_count")

    def __init__(
        self,
        sources: list[Source],
        passages: list[str],
        top_score: float,
        all_candidates_count: int,
        kept_count: int,
    ) -> None:
        self.sources = sources
        self.passages = passages
        self.top_score = top_score
        self.all_candidates_count = all_candidates_count
        self.kept_count = kept_count

    @property
    def has_evidence(self) -> bool:
        """True when at least one chunk passed the score threshold."""
        return self.kept_count > 0


# ── Validation ────────────────────────────────────────────────────────────────

def normalize_question(question: str) -> str:
    """
    Trim, collapse internal whitespace, and validate length.

    Returns the cleaned question string.

    Raises:
        ValueError: If the question is empty or exceeds QUESTION_MAX_LEN after
                    normalization.
    """
    cleaned = question.strip()
    cleaned = _COLLAPSE_WHITESPACE.sub(" ", cleaned)

    if len(cleaned) < QUESTION_MIN_LEN:
        raise ValueError("Question must not be empty.")
    if len(cleaned) > QUESTION_MAX_LEN:
        raise ValueError(
            f"Question is too long ({len(cleaned)} chars); "
            f"maximum is {QUESTION_MAX_LEN}."
        )
    return cleaned


# ── Core retrieval ────────────────────────────────────────────────────────────

async def retrieve_candidates(
    question: str,
    top_k: int | None = None,
    *,
    embed_client: genai.Client | None = None,
    qdrant_client: AsyncQdrantClient | None = None,
) -> list[dict]:
    """
    Embed the question and return raw Qdrant hits WITHOUT threshold filtering.

    Used by the evaluation script to see the full score distribution.

    Returns:
        List of dicts, each with keys:
          score, title, section, path, source_file, module, text, chunk_index
        Sorted by score descending.

    Raises:
        NotConfiguredError, EmbeddingError, RetrievalError.
    """
    settings = get_settings()
    top_k = top_k if top_k is not None else settings.rag_top_k

    question = normalize_question(question)

    # Embed with task type RETRIEVAL_QUERY
    query_vector = await emb_service.embed_query(question, client=embed_client)

    # Search with score_threshold=0.0 to return ALL candidates
    hits = await qdrant_service.search_similar(
        query_vector=query_vector,
        top_k=top_k,
        score_threshold=0.0,
        client=qdrant_client,
    )

    results = []
    for hit in hits:
        payload = hit.payload or {}
        results.append({
            "score": round(hit.score, 5),
            "title": payload.get("title", ""),
            "section": payload.get("section", ""),
            "path": payload.get("path", ""),
            "source_file": payload.get("source_file", ""),
            "module": payload.get("module", ""),
            "text": payload.get("text", ""),
            "chunk_index": payload.get("chunk_index", 0),
        })

    return results


async def retrieve(
    question: str,
    *,
    embed_client: genai.Client | None = None,
    qdrant_client: AsyncQdrantClient | None = None,
) -> RetrievalResult:
    """
    Full retrieval pipeline: validate → embed → search → threshold filter.

    Args:
        question:      Raw question string (will be normalized internally).
        embed_client:  Optional pre-built Gemini client for testing.
        qdrant_client: Optional pre-built Qdrant client for testing.

    Returns:
        RetrievalResult.  If no chunks pass the threshold, ``has_evidence``
        is False and sources/passages are empty — the caller MUST return the
        refusal message without calling the generation model.

    Raises:
        ValueError:         Invalid question (too short / too long).
        NotConfiguredError: Google or Qdrant are not configured.
        EmbeddingError:     Embedding API call failed.
        RetrievalError:     Qdrant search failed.
    """
    settings = get_settings()

    # 1. Normalize and validate
    clean_q = normalize_question(question)
    logger.debug("retrieve: question_length=%d", len(clean_q))

    # 2. Embed (RETRIEVAL_QUERY task type)
    query_vector = await emb_service.embed_query(clean_q, client=embed_client)

    # 3. Fetch top-K candidates from Qdrant WITHOUT threshold so we can log
    #    the full score range before filtering
    all_hits = await qdrant_service.search_similar(
        query_vector=query_vector,
        top_k=settings.rag_top_k,
        score_threshold=0.0,        # fetch all; filter below
        client=qdrant_client,
    )

    all_count = len(all_hits)
    top_score = all_hits[0].score if all_hits else 0.0

    # 4. Apply configurable score threshold
    threshold = settings.rag_score_threshold
    kept_hits = [h for h in all_hits if h.score >= threshold]
    kept_count = len(kept_hits)

    logger.info(
        "retrieve: candidates=%d  top_score=%.4f  threshold=%.3f  kept=%d",
        all_count,
        top_score,
        threshold,
        kept_count,
    )

    # 5. Build result objects
    sources: list[Source] = []
    passages: list[str] = []

    for hit in kept_hits:
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

    return RetrievalResult(
        sources=sources,
        passages=passages,
        top_score=round(top_score, 5),
        all_candidates_count=all_count,
        kept_count=kept_count,
    )
