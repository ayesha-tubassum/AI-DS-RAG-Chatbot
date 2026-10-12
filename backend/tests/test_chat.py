"""
Tests for POST /api/chat.

All external services (Gemini, Qdrant) are mocked — no real API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.core.errors import NotConfiguredError
from app.prompts.rag_prompt import REFUSAL_MESSAGE
from app.schemas import ChatResponse

client = TestClient(app)


# ── Input validation ──────────────────────────────────────────────────────────

def test_empty_question_rejected():
    response = client.post("/api/chat", json={"question": ""})
    assert response.status_code == 422


def test_whitespace_only_question_rejected():
    """Whitespace-only strings become empty after strip, which triggers min_length."""
    response = client.post("/api/chat", json={"question": "   "})
    assert response.status_code == 422


def test_question_too_long_rejected():
    response = client.post("/api/chat", json={"question": "a" * 1001})
    assert response.status_code == 422


def test_max_length_question_accepted():
    """A question exactly at the 1000-char limit must pass validation."""
    with patch(
        "app.api.chat.rag_service.answer",
        new_callable=AsyncMock,
        return_value=ChatResponse(
            answer=REFUSAL_MESSAGE, grounded=False, sources=[]
        ),
    ):
        response = client.post("/api/chat", json={"question": "a" * 1000})
    assert response.status_code == 200


def test_missing_question_field_rejected():
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


# ── Refusal when no evidence found ───────────────────────────────────────────

def test_refusal_returned_when_no_evidence():
    """When rag_service returns grounded=False, the exact refusal message is returned."""
    refusal_response = ChatResponse(
        answer=REFUSAL_MESSAGE, grounded=False, sources=[]
    )
    with patch(
        "app.api.chat.rag_service.answer",
        new_callable=AsyncMock,
        return_value=refusal_response,
    ):
        response = client.post("/api/chat", json={"question": "What is quantum computing?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == REFUSAL_MESSAGE
    assert data["grounded"] is False
    assert data["sources"] == []


def test_refusal_message_exact_text():
    """The refusal constant itself must match the required wording."""
    assert "I can only answer questions" in REFUSAL_MESSAGE
    assert "AI and Data Science" in REFUSAL_MESSAGE
    assert "could not find enough relevant information" in REFUSAL_MESSAGE


# ── NotConfiguredError → 503 ─────────────────────────────────────────────────

def test_not_configured_returns_503():
    with patch(
        "app.api.chat.rag_service.answer",
        new_callable=AsyncMock,
        side_effect=NotConfiguredError("Gemini embeddings", ["GOOGLE_API_KEY"]),
    ):
        response = client.post("/api/chat", json={"question": "What is pandas?"})

    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    # Secret values must NOT appear in the response.
    assert "GOOGLE_API_KEY" not in data["detail"]


def test_503_does_not_leak_api_key():
    with patch(
        "app.api.chat.rag_service.answer",
        new_callable=AsyncMock,
        side_effect=NotConfiguredError("Qdrant vector search", ["QDRANT_API_KEY"]),
    ):
        response = client.post("/api/chat", json={"question": "Hello"})

    assert response.status_code == 503
    # The raw key name should not be echoed back.
    assert "QDRANT_API_KEY" not in response.text


# ── Unexpected errors → 500, no stack trace ───────────────────────────────────

def test_unhandled_exception_returns_500():
    with patch(
        "app.api.chat.rag_service.answer",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Something blew up"),
    ):
        response = client.post("/api/chat", json={"question": "Hello"})

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    # Stack trace and internal message must not leak.
    assert "Something blew up" not in data["detail"]
    assert "Traceback" not in data["detail"]
