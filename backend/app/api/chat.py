"""POST /api/chat — RAG chat endpoint."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.errors import (
    EmbeddingError,
    GenerationError,
    NotConfiguredError,
    RetrievalError,
)
from app.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error (e.g. empty question)"},
        503: {"model": ErrorResponse, "description": "A required service is not configured"},
        500: {"model": ErrorResponse, "description": "Unexpected internal error"},
    },
    summary="Ask a question about the book",
    tags=["chat"],
)
async def chat(request: ChatRequest) -> ChatResponse | JSONResponse:
    """
    Accept a user question, run the RAG pipeline, and return an answer.

    - The question must be 1–1000 non-whitespace characters.
    - If no relevant content is found the refusal message is returned with
      ``grounded: false`` and an empty ``sources`` list.
    - Stack traces and secret values are never included in error responses.
    """
    try:
        return await rag_service.answer(request.question)

    except NotConfiguredError as exc:
        # A required service (Google / Qdrant) is not set up yet.
        # Log the full message server-side; return a safe summary to the caller.
        logger.warning("Service not configured: %s", exc.feature)
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                detail=f"The '{exc.feature}' service is not available. "
                "Please check the server configuration."
            ).model_dump(),
        )

    except (EmbeddingError, RetrievalError, GenerationError) as exc:
        logger.error("Pipeline error: %s", type(exc).__name__, exc_info=True)
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                detail="The chat service encountered an error. Please try again later."
            ).model_dump(),
        )

    except Exception:
        logger.exception("Unhandled exception in /api/chat")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(detail="An unexpected error occurred.").model_dump(),
        )
