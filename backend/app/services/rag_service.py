"""
RAG orchestration service.

Flow:
  1. Embed the question (raises NotConfiguredError if Google key is missing).
  2. Search Qdrant (raises NotConfiguredError if Qdrant is not configured).
  3. If no evidence meets the score threshold → return the refusal response
     WITHOUT calling the generation model.
  4. Build a prompt from retrieved passages and call Gemini for the answer.
  5. Return ChatResponse with answer, grounded=True, and sources.
"""

import logging

from google import genai
from google.genai import types

from app.config import get_settings
from app.core.errors import GenerationError, NotConfiguredError
from app.prompts.rag_prompt import REFUSAL_MESSAGE, RAG_SYSTEM_PROMPT
from app.schemas import ChatResponse, Source
from app.services.retrieval import retrieve

logger = logging.getLogger(__name__)


def _get_gemini_client() -> genai.Client:
    settings = get_settings()
    if not settings.google_configured:
        raise NotConfiguredError("Answer generation", ["GOOGLE_API_KEY"])
    return genai.Client(api_key=settings.google_api_key)


async def answer(question: str) -> ChatResponse:
    """
    Run the full RAG pipeline for a user question.

    Args:
        question: The validated, stripped user question.

    Returns:
        ChatResponse with answer text, grounded flag, and sources list.

    Raises:
        NotConfiguredError: If required services are not configured.
        EmbeddingError: If embedding fails.
        RetrievalError: If vector search fails.
        GenerationError: If the Gemini generation call fails.
    """
    settings = get_settings()

    # ── Step 1 + 2: embed + retrieve (with threshold applied) ────────────
    result = await retrieve(question)

    # ── Step 3: no evidence — refuse without calling generation ──────────
    if not result.has_evidence:
        logger.info("No evidence found; returning refusal.")
        return ChatResponse(
            answer=REFUSAL_MESSAGE,
            grounded=False,
            sources=[],
        )

    # ── Step 4: build prompt and call Gemini ─────────────────────────────
    context_block = "\n\n---\n\n".join(
        f"[{s.title} — {s.section}]\n{p}" if s.section else f"[{s.title}]\n{p}"
        for s, p in zip(result.sources, result.passages)
    )

    prompt = RAG_SYSTEM_PROMPT.format(context=context_block, question=question)

    client = _get_gemini_client()
    try:
        response = await client.aio.models.generate_content(
            model=settings.generation_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
            ),
        )
    except Exception as exc:
        logger.error("Generation API call failed: %s", type(exc).__name__)
        raise GenerationError(str(exc)) from exc

    answer_text = response.text or REFUSAL_MESSAGE
    grounded = answer_text != REFUSAL_MESSAGE

    # ── Step 5: return response ───────────────────────────────────────────
    return ChatResponse(
        answer=answer_text,
        grounded=grounded,
        sources=result.sources if grounded else [],
    )
