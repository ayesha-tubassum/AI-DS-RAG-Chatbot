"""
RAG orchestration service.

Flow:
  Gate 1 (retrieval gate):
    Embed the question and retrieve top-K chunks.
    If the result is EMPTY (nothing passes RAG_SCORE_THRESHOLD) → return the
    exact refusal immediately WITHOUT calling the generation model.

  Gate 2 (evidence sufficiency + grounded answer):
    One generation call with structured JSON output.
    The model returns {"supported": bool, "answer": str, "used_chunks": [int]}.
    • supported=false  → return refusal, no sources
    • supported=true   → return answer + sources filtered to used_chunks only
    • JSON invalid/unparseable → return refusal (safe fallback)

Security:
  Chunk text is treated as DATA in the prompt.  Any instruction-like text
  inside a chunk (e.g. "ignore previous instructions") is ignored by design —
  the prompt wraps data in explicit DATA BLOCK markers and tells the model
  to treat all embedded text as literal data only.

Retry:
  429 rate-limit errors from the Gemini API are retried with exponential
  backoff before propagating as GenerationError.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import APIError as GeminiAPIError
from pydantic import BaseModel, ValidationError

from app.config import get_settings
from app.core.errors import GenerationError, NotConfiguredError
from app.prompts.rag_prompt import GENERATION_PROMPT, REFUSAL_MESSAGE
from app.schemas import ChatResponse, Source
from app.services.retrieval import RetrievalResult, retrieve

logger = logging.getLogger(__name__)

# ── Retry constants ────────────────────────────────────────────────────────────
_RETRY_DELAYS = (2.0, 4.0, 8.0)          # seconds between attempts
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


# ── Structured output schema ───────────────────────────────────────────────────

class _GenerationResponse(BaseModel):
    """
    Schema for the single JSON generation call.

    supported:   True iff the retrieved chunks directly answer the question.
    answer:      The answer text (empty string when supported=False).
    used_chunks: Indexes into the retrieved chunk list that the model used.
    """
    supported: bool
    answer: str
    used_chunks: list[int]


# ── Client factory ─────────────────────────────────────────────────────────────

def _get_client() -> genai.Client:
    settings = get_settings()
    if not settings.google_configured:
        raise NotConfiguredError("Answer generation", ["GOOGLE_API_KEY"])
    return genai.Client(api_key=settings.google_api_key)  # type: ignore[arg-type]


# ── Generation with retry ──────────────────────────────────────────────────────

async def _generate_with_retry(
    client: genai.Client,
    model: str,
    prompt: str,
) -> _GenerationResponse | None:
    """
    Call the Gemini model and parse the structured JSON response.

    Returns a validated _GenerationResponse, or None if the response
    is unparseable / invalid (caller treats this as supported=False).

    Retries on 429 / 5xx up to len(_RETRY_DELAYS)+1 attempts.

    Raises:
        GenerationError: Non-retryable API error or all retries exhausted.
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=_GenerationResponse,
        temperature=0.1,          # deterministic — eliminates supported=false flips
        max_output_tokens=1024,
    )

    last_exc: Exception | None = None
    for attempt, delay in enumerate((*_RETRY_DELAYS, None), start=1):
        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            break   # success
        except GeminiAPIError as exc:
            code = getattr(exc, "code", None)
            if code in _RETRYABLE_STATUS_CODES and delay is not None:
                logger.warning(
                    "Generation attempt %d failed (status=%s); retrying in %.0fs",
                    attempt, code, delay,
                )
                await asyncio.sleep(delay)
                last_exc = exc
                continue
            raise GenerationError(
                f"Gemini API error (status={code})"
            ) from exc
        except Exception as exc:
            raise GenerationError(
                f"Unexpected error during generation: {type(exc).__name__}"
            ) from exc
    else:
        raise GenerationError(
            f"Generation failed after {len(_RETRY_DELAYS) + 1} attempts."
        ) from last_exc

    # Try .parsed first (SDK-validated Pydantic object)
    if response.parsed is not None and isinstance(response.parsed, _GenerationResponse):
        return response.parsed

    # Fallback: parse .text manually
    raw = response.text or ""
    if not raw.strip():
        logger.warning("Generation returned empty text; treating as unsupported.")
        return None

    try:
        data = json.loads(raw)
        return _GenerationResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.warning(
            "Generation returned invalid JSON (%s); treating as unsupported.",
            type(exc).__name__,
        )
        return None


# ── Source deduplication ───────────────────────────────────────────────────────

def _build_sources(
    retrieval_result: RetrievalResult,
    used_chunks: list[int],
) -> list[Source]:
    """
    Build the deduplicated source list from the used_chunks indexes.

    • Validates each index against the retrieved chunks (ignores out-of-range).
    • Deduplicates by (path, section) — keeps the first occurrence (highest score
      since chunks are sorted descending).
    • Never invents paths; takes them only from the retrieval payload.
    """
    sources = retrieval_result.sources
    seen: set[tuple[str, str]] = set()
    result: list[Source] = []

    for idx in used_chunks:
        if not isinstance(idx, int) or idx < 0 or idx >= len(sources):
            logger.debug("Ignoring invalid used_chunk index %r", idx)
            continue
        src = sources[idx]
        key = (src.path, src.section)
        if key in seen:
            continue
        seen.add(key)
        result.append(src)

    return result


# ── Main entry point ───────────────────────────────────────────────────────────

async def answer(question: str) -> ChatResponse:
    """
    Full RAG pipeline: Gate 1 (retrieval) + Gate 2 (grounded generation).

    Args:
        question: The validated, stripped user question (from the API layer).

    Returns:
        ChatResponse with answer text, grounded flag, and sources list.

    Raises:
        NotConfiguredError: Google or Qdrant are not configured.
        EmbeddingError:     Embedding the question failed.
        RetrievalError:     Qdrant search failed.
        GenerationError:    Generation API call failed after all retries.
    """
    settings = get_settings()

    # ── Gate 1: retrieval ─────────────────────────────────────────────────────
    retrieval_result: RetrievalResult = await retrieve(question)

    if not retrieval_result.has_evidence:
        logger.info(
            "answer: gate1=FAIL  question_len=%d  top_score=%.4f  → refusal",
            len(question),
            retrieval_result.top_score,
        )
        return ChatResponse(answer=REFUSAL_MESSAGE, grounded=False, sources=[])

    logger.info(
        "answer: gate1=PASS  retrieved=%d  top_score=%.4f",
        retrieval_result.kept_count,
        retrieval_result.top_score,
    )

    # ── Gate 2: grounded generation ───────────────────────────────────────────
    # Build numbered chunk list for the prompt.
    # IMPORTANT: use original_question (no suffix) for the generation prompt.
    numbered_chunks_parts: list[str] = []
    for i, (src, passage) in enumerate(
        zip(retrieval_result.sources, retrieval_result.passages)
    ):
        header = f"[{i}] {src.title}"
        if src.section:
            header += f" — {src.section}"
        numbered_chunks_parts.append(f"{header}\n{passage}")

    numbered_chunks = "\n\n".join(numbered_chunks_parts)
    prompt = GENERATION_PROMPT.format(
        numbered_chunks=numbered_chunks,
        question=retrieval_result.original_question,   # ← original, no suffix
    )

    client = _get_client()
    gen_response = await _generate_with_retry(
        client=client,
        model=settings.generation_model,
        prompt=prompt,
    )

    # ── Evaluate generation result ─────────────────────────────────────────────
    if gen_response is None or not gen_response.supported:
        logger.info(
            "answer: gate2=FAIL  supported=%s  → refusal",
            None if gen_response is None else gen_response.supported,
        )
        return ChatResponse(answer=REFUSAL_MESSAGE, grounded=False, sources=[])

    sources = _build_sources(retrieval_result, gen_response.used_chunks)

    logger.info(
        "answer: gate2=PASS  supported=True  sources=%d",
        len(sources),
    )

    return ChatResponse(
        answer=gen_response.answer,
        grounded=True,
        sources=sources,
    )
