"""
Tests for app/services/retrieval.py.

All external services (Gemini, Qdrant) are mocked — no real API calls.
"""

from __future__ import annotations

import math
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.config import Settings
from app.core.errors import NotConfiguredError, RetrievalError, EmbeddingError
from app.services.retrieval import (
    QUESTION_MAX_LEN,
    RetrievalResult,
    normalize_question,
    retrieve,
    retrieve_candidates,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _unit_vec(n: int = 3072) -> list[float]:
    val = 1.0 / math.sqrt(n)
    return [val] * n


def _make_scored_point(score: float, payload: dict) -> MagicMock:
    pt = MagicMock()
    pt.score = score
    pt.payload = payload
    return pt


def _make_payload(
    title: str = "Test Title",
    section: str = "Test Section",
    path: str = "/test/page",
    source_file: str = "module-01/test.md",
    module: str = "module-01-python-foundations",
    text: str = "Some content text here.",
    chunk_index: int = 0,
) -> dict:
    return {
        "title": title,
        "section": section,
        "path": path,
        "source_file": source_file,
        "module": module,
        "text": text,
        "chunk_index": chunk_index,
    }


# Settings without .env so tests are hermetic
_NO_KEY_SETTINGS = Settings(
    _env_file=None,  # type: ignore[call-arg]
    google_api_key=None,
    qdrant_url=None,
    qdrant_api_key=None,
    rag_top_k=5,
    rag_score_threshold=0.5,
)

_WITH_KEYS_SETTINGS = Settings(
    _env_file=None,  # type: ignore[call-arg]
    google_api_key="fake-google-key",
    qdrant_url="https://fake.qdrant.io:6333",
    qdrant_api_key="fake-qdrant-key",
    rag_top_k=5,
    rag_score_threshold=0.5,
    embedding_model="gemini-embedding-001",
    embedding_dimension=3072,
)


# ── normalize_question ─────────────────────────────────────────────────────────

class TestNormalizeQuestion:
    def test_strips_leading_trailing_whitespace(self):
        assert normalize_question("  hello  ") == "hello"

    def test_collapses_internal_whitespace(self):
        assert normalize_question("what  is  a   variable?") == "what is a variable?"

    def test_collapses_newlines(self):
        assert normalize_question("what\nis\na\nvariable?") == "what is a variable?"

    def test_empty_after_strip_raises(self):
        with pytest.raises(ValueError, match="empty"):
            normalize_question("   ")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="too long"):
            normalize_question("a" * (QUESTION_MAX_LEN + 1))

    def test_exactly_max_length_ok(self):
        q = "a" * QUESTION_MAX_LEN
        assert normalize_question(q) == q

    def test_single_word_ok(self):
        assert normalize_question("Python") == "Python"


# ── retrieve: threshold filtering ─────────────────────────────────────────────

class TestRetrieveThreshold:
    """Mock embed_query and search_similar; test threshold behaviour."""

    @pytest.fixture(autouse=True)
    def patch_settings(self):
        with patch("app.services.retrieval.get_settings", return_value=_WITH_KEYS_SETTINGS):
            with patch("app.services.qdrant_service.get_settings", return_value=_WITH_KEYS_SETTINGS):
                yield

    @pytest.mark.asyncio
    async def test_keeps_results_above_threshold(self):
        hits = [
            _make_scored_point(0.85, _make_payload(title="High Score")),
            _make_scored_point(0.72, _make_payload(title="Also High")),
            _make_scored_point(0.30, _make_payload(title="Too Low")),
        ]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            result = await retrieve("What is Python?")

        # threshold=0.5, so 0.85 and 0.72 kept; 0.30 dropped
        assert result.kept_count == 2
        assert result.all_candidates_count == 3
        assert result.has_evidence is True
        assert len(result.sources) == 2
        assert result.sources[0].title == "High Score"
        assert result.sources[1].title == "Also High"

    @pytest.mark.asyncio
    async def test_empty_result_when_nothing_passes_threshold(self):
        hits = [
            _make_scored_point(0.30, _make_payload()),
            _make_scored_point(0.25, _make_payload()),
        ]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            result = await retrieve("What is Python?")

        assert result.has_evidence is False
        assert result.sources == []
        assert result.passages == []
        assert result.kept_count == 0

    @pytest.mark.asyncio
    async def test_empty_result_when_no_qdrant_hits(self):
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=[]):

            result = await retrieve("What is Python?")

        assert result.has_evidence is False
        assert result.top_score == 0.0

    @pytest.mark.asyncio
    async def test_results_sorted_by_score_descending(self):
        # Qdrant returns them in order, but verify source order preserved
        hits = [
            _make_scored_point(0.90, _make_payload(title="First")),
            _make_scored_point(0.80, _make_payload(title="Second")),
            _make_scored_point(0.70, _make_payload(title="Third")),
        ]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            result = await retrieve("What is Python?")

        titles = [s.title for s in result.sources]
        assert titles == ["First", "Second", "Third"]

    @pytest.mark.asyncio
    async def test_top_score_reported_correctly(self):
        hits = [
            _make_scored_point(0.91, _make_payload()),
            _make_scored_point(0.62, _make_payload()),
        ]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            result = await retrieve("What is Python?")

        assert abs(result.top_score - 0.91) < 0.001


# ── retrieve: payload fields ───────────────────────────────────────────────────

class TestRetrievePayloadFields:
    @pytest.fixture(autouse=True)
    def patch_settings(self):
        with patch("app.services.retrieval.get_settings", return_value=_WITH_KEYS_SETTINGS):
            with patch("app.services.qdrant_service.get_settings", return_value=_WITH_KEYS_SETTINGS):
                yield

    @pytest.mark.asyncio
    async def test_all_payload_fields_present_in_source(self):
        payload = _make_payload(
            title="Variables and Data Types",
            section="Python variables",
            path="/module-01-python-foundations/variables-data-types",
            source_file="module-01-python-foundations/01-variables-data-types.md",
            module="module-01-python-foundations",
            text="A variable is a named storage location.",
        )
        hits = [_make_scored_point(0.88, payload)]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            result = await retrieve("What is a variable?")

        assert len(result.sources) == 1
        src = result.sources[0]
        assert src.title == "Variables and Data Types"
        assert src.section == "Python variables"
        assert src.path == "/module-01-python-foundations/variables-data-types"
        assert src.score == 0.88

    @pytest.mark.asyncio
    async def test_passage_text_matches_payload(self):
        text = "A variable stores a value in memory."
        hits = [_make_scored_point(0.88, _make_payload(text=text))]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            result = await retrieve("What is a variable?")

        assert result.passages[0] == text

    @pytest.mark.asyncio
    async def test_missing_text_payload_excluded_from_passages(self):
        """A hit with empty/missing text should not add an empty passage."""
        hits = [_make_scored_point(0.88, _make_payload(text=""))]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            result = await retrieve("What is a variable?")

        assert result.passages == []
        # Source is still present even if text is empty
        assert len(result.sources) == 1


# ── retrieve: error propagation ────────────────────────────────────────────────

class TestRetrieveErrors:
    @pytest.fixture(autouse=True)
    def patch_settings(self):
        with patch("app.services.retrieval.get_settings", return_value=_WITH_KEYS_SETTINGS):
            with patch("app.services.qdrant_service.get_settings", return_value=_WITH_KEYS_SETTINGS):
                yield

    @pytest.mark.asyncio
    async def test_not_configured_propagates(self):
        no_key = Settings(
            _env_file=None,  # type: ignore[call-arg]
            google_api_key=None,
        )
        with patch("app.services.retrieval.get_settings", return_value=no_key), \
             patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock,
                   side_effect=NotConfiguredError("Gemini", ["GOOGLE_API_KEY"])):
            with pytest.raises(NotConfiguredError):
                await retrieve("What is Python?")

    @pytest.mark.asyncio
    async def test_retrieval_error_propagates(self):
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, side_effect=RetrievalError("connection refused")):
            with pytest.raises(RetrievalError):
                await retrieve("What is Python?")

    def test_empty_question_raises(self):
        with pytest.raises(ValueError):
            normalize_question("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            normalize_question("   \t\n  ")


# ── retrieve: no generation call ──────────────────────────────────────────────

class TestNoGenerationCall:
    """Retrieval must NEVER call rag_service or any generation model."""

    @pytest.fixture(autouse=True)
    def patch_settings(self):
        with patch("app.services.retrieval.get_settings", return_value=_WITH_KEYS_SETTINGS):
            with patch("app.services.qdrant_service.get_settings", return_value=_WITH_KEYS_SETTINGS):
                yield

    @pytest.mark.asyncio
    async def test_no_generate_content_call(self):
        hits = [_make_scored_point(0.9, _make_payload())]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits), \
             patch("app.services.retrieval.genai") as mock_genai:

            await retrieve("What is Python?")

        # The genai client must never have generate_content called
        mock_genai.Client.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_generate_when_below_threshold(self):
        """Even on a miss, generation must not be called."""
        hits = [_make_scored_point(0.1, _make_payload())]  # below threshold
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits), \
             patch("app.services.retrieval.genai") as mock_genai:

            result = await retrieve("What is biryani?")

        assert result.has_evidence is False
        mock_genai.Client.assert_not_called()


# ── retrieve_candidates: no threshold ─────────────────────────────────────────

class TestRetrieveCandidates:
    @pytest.fixture(autouse=True)
    def patch_settings(self):
        with patch("app.services.retrieval.get_settings", return_value=_WITH_KEYS_SETTINGS):
            with patch("app.services.qdrant_service.get_settings", return_value=_WITH_KEYS_SETTINGS):
                yield

    @pytest.mark.asyncio
    async def test_returns_all_including_low_scores(self):
        hits = [
            _make_scored_point(0.85, _make_payload(title="High")),
            _make_scored_point(0.20, _make_payload(title="Low")),
        ]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            candidates = await retrieve_candidates("What is Python?")

        assert len(candidates) == 2
        assert candidates[0]["score"] == 0.85
        assert candidates[1]["score"] == 0.20

    @pytest.mark.asyncio
    async def test_candidate_dict_has_required_fields(self):
        payload = _make_payload(title="T", section="S", path="/p", module="m")
        hits = [_make_scored_point(0.70, payload)]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):

            candidates = await retrieve_candidates("test")

        c = candidates[0]
        for field in ("score", "title", "section", "path", "source_file", "module", "text", "chunk_index"):
            assert field in c, f"Missing field: {field}"
