"""
Retrieval service: validate → (optionally expand) → embed → search Qdrant → filter → return.

Short-query expansion
---------------------
Queries of 6 words or fewer get a domain suffix appended ONLY for the embedding/search
step.  The suffix is never shown to the user and is NOT passed to the generation model.

  "what is float"
  → embedded as:
  "what is float (in the context of Python, data science, machine learning and AI)"

The word count ignores a trailing question mark (so "what is float?" is treated the
same as "what is float" — both are 3 words).

The suffix is defined as SHORT_QUERY_SUFFIX below so it can be changed in one place.

Design
------
- Does NOT generate any answer. Stays separately testable.
- Embedding and Qdrant clients are injectable for unit tests.
- Score threshold filtering happens here (not inside qdrant_service) so the
  evaluation script can call retrieve_candidates() without a threshold and
  apply its own cutoff.
- Diagnostic logging: question length, search text length, number of candidates,
  top score, number kept. Secret values (API keys) are never logged.
"""

from __future__ import annotations

import logging
import re

from google import genai
from qdrant_client import AsyncQdrantClient

from app.config import get_settings
from app.core.errors import EmbeddingError, NotConfiguredError, RetrievalError
from app.schemas import Source
from app.services import embeddings as emb_service
from app.services import qdrant_service

logger = logging.getLogger(__name__)

# ── Question validation constants ──────────────────────────────────────────────
QUESTION_MIN_LEN = 1
QUESTION_MAX_LEN = 1000
_COLLAPSE_WHITESPACE = re.compile(r"\s+")

# ── Short-query expansion ──────────────────────────────────────────────────────
# Queries with this many words or fewer get the domain suffix appended before
# embedding.  Word count is computed on the question WITHOUT a trailing "?".
SHORT_QUERY_WORD_LIMIT: int = 6

# The suffix added to short queries.  Change this one constant to adjust it.
SHORT_QUERY_SUFFIX: str = (
    "(in the context of Python, data science, machine learning and AI)"
)


# ── Public result type ─────────────────────────────────────────────────────────

class RetrievalResult:
    """
    Outcome of a retrieval call.

    Attributes:
        sources:              Metadata for each kept chunk (used in the API response).
        passages:             Raw text for each kept chunk (used to build the RAG prompt).
        original_question:    The user's question exactly as normalised — no suffix.
                              rag_service must pass this to the generation model.
        search_text:          The text that was actually embedded (may have the suffix).
        top_score:            Score of the highest-ranked result (0.0 if no candidates).
        all_candidates_count: Total candidates returned by Qdrant before threshold.
        kept_count:           Number of results that passed the score threshold.
    """

    __slots__ = (
        "sources",
        "passages",
        "original_question",
        "search_text",
        "top_score",
        "all_candidates_count",
        "kept_count",
    )

    def __init__(
        self,
        sources: list[Source],
        passages: list[str],
        original_question: str,
        search_text: str,
        top_score: float,
        all_candidates_count: int,
        kept_count: int,
    ) -> None:
        self.sources             = sources
        self.passages            = passages
        self.original_question   = original_question
        self.search_text         = search_text
        self.top_score           = top_score
        self.all_candidates_count = all_candidates_count
        self.kept_count          = kept_count

    @property
    def has_evidence(self) -> bool:
        """True when at least one chunk passed the score threshold."""
        return self.kept_count > 0


# ── Validation ─────────────────────────────────────────────────────────────────

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


# ── Short-query expansion ──────────────────────────────────────────────────────

def _word_count_for_expansion(question: str) -> int:
    """
    Count words for the expansion rule.

    A trailing question mark on the last word is stripped before counting so
    "what is float?" and "what is float" both yield 3 words.
    """
    stripped = question.rstrip("?").strip()
    return len(stripped.split())


def build_search_text(question: str) -> str:
    """
    Return the text to embed for retrieval.

    Short questions (≤ SHORT_QUERY_WORD_LIMIT words, trailing ? ignored)
    get the domain suffix appended.  Longer questions are returned unchanged.

    The caller is responsible for normalizing the question first.
    """
    if _word_count_for_expansion(question) <= SHORT_QUERY_WORD_LIMIT:
        return f"{question} {SHORT_QUERY_SUFFIX}"
    return question


# ── Core retrieval ─────────────────────────────────────────────────────────────

async def retrieve_candidates(
    question: str,
    top_k: int | None = None,
    *,
    embed_client: genai.Client | None = None,
    qdrant_client: AsyncQdrantClient | None = None,
) -> list[dict]:
    """
    Embed the question (with expansion if short) and return raw Qdrant hits
    WITHOUT threshold filtering.

    Used by the evaluation script to see the full score distribution.

    Returns:
        List of dicts sorted by score descending, each with keys:
          score, title, section, path, source_file, module, text, chunk_index
    """
    settings = get_settings()
    top_k = top_k if top_k is not None else settings.rag_top_k

    question    = normalize_question(question)
    search_text = build_search_text(question)

    query_vector = await emb_service.embed_query(search_text, client=embed_client)

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
            "score":        round(hit.score, 5),
            "title":        payload.get("title", ""),
            "section":      payload.get("section", ""),
            "path":         payload.get("path", ""),
            "source_file":  payload.get("source_file", ""),
            "module":       payload.get("module", ""),
            "text":         payload.get("text", ""),
            "chunk_index":  payload.get("chunk_index", 0),
        })

    return results


async def retrieve(
    question: str,
    *,
    embed_client: genai.Client | None = None,
    qdrant_client: AsyncQdrantClient | None = None,
) -> RetrievalResult:
    """
    Full retrieval pipeline: validate → expand → embed → search → threshold filter.

    The ORIGINAL question (without any suffix) is stored on the returned
    RetrievalResult.original_question.  rag_service MUST use that field when
    building the generation prompt — never the expanded search text.

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

    # 1. Normalize — this is the original question we keep
    original = normalize_question(question)

    # 2. Build search text (may have domain suffix for short queries)
    search_text = build_search_text(original)

    expanded = search_text != original
    logger.debug(
        "retrieve: original_len=%d  search_len=%d  expanded=%s",
        len(original), len(search_text), expanded,
    )

    # 3. Embed the SEARCH TEXT (not the original)
    query_vector = await emb_service.embed_query(search_text, client=embed_client)

    # 4. Fetch top-K candidates WITHOUT threshold so we can log before filtering
    all_hits = await qdrant_service.search_similar(
        query_vector=query_vector,
        top_k=settings.rag_top_k,
        score_threshold=0.0,
        client=qdrant_client,
    )

    all_count = len(all_hits)
    top_score = all_hits[0].score if all_hits else 0.0

    # 5. Apply configurable score threshold
    threshold  = settings.rag_score_threshold
    kept_hits  = [h for h in all_hits if h.score >= threshold]
    kept_count = len(kept_hits)

    logger.info(
        "retrieve: candidates=%d  top_score=%.4f  threshold=%.3f  kept=%d  expanded=%s",
        all_count,
        top_score,
        threshold,
        kept_count,
        expanded,
    )

    # 6. Build result objects
    sources:  list[Source] = []
    passages: list[str]    = []

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
        original_question=original,       # ← ORIGINAL, no suffix
        search_text=search_text,          # ← what was embedded (may have suffix)
        top_score=round(top_score, 5),
        all_candidates_count=all_count,
        kept_count=kept_count,
    )
