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


# ── Query expansion ────────────────────────────────────────────────────────────

from app.services.retrieval import (
    SHORT_QUERY_SUFFIX,
    SHORT_QUERY_WORD_LIMIT,
    build_search_text,
    _word_count_for_expansion,
)


class TestQueryExpansion:
    """Unit tests for the short-query expansion logic — no mocks needed."""

    # ── build_search_text ──────────────────────────────────────────────────────

    def test_short_query_gets_suffix(self):
        result = build_search_text("what is float")
        assert result == f"what is float {SHORT_QUERY_SUFFIX}"

    def test_long_query_unchanged(self):
        q = "What is the difference between supervised and unsupervised learning?"
        assert build_search_text(q) == q

    def test_exactly_at_limit_gets_suffix(self):
        # 6 words — at the limit, should expand
        q = "one two three four five six"
        assert q not in build_search_text(q) or SHORT_QUERY_SUFFIX in build_search_text(q)
        result = build_search_text(q)
        assert result.endswith(SHORT_QUERY_SUFFIX)

    def test_one_over_limit_unchanged(self):
        # 7 words — just over the limit
        q = "one two three four five six seven"
        assert build_search_text(q) == q

    def test_trailing_question_mark_ignored_for_count(self):
        # "what is float?" = 3 words (? stripped), should still expand
        q = "what is float?"
        result = build_search_text(q)
        assert SHORT_QUERY_SUFFIX in result

    def test_no_question_mark_short_gets_suffix(self):
        assert SHORT_QUERY_SUFFIX in build_search_text("what is pandas")

    def test_suffix_is_named_constant(self):
        # Verify the constant is importable and non-empty
        assert isinstance(SHORT_QUERY_SUFFIX, str)
        assert len(SHORT_QUERY_SUFFIX) > 0

    # ── _word_count_for_expansion ─────────────────────────────────────────────

    def test_word_count_strips_trailing_question_mark(self):
        assert _word_count_for_expansion("what is float?") == 3

    def test_word_count_no_question_mark(self):
        assert _word_count_for_expansion("what is float") == 3

    def test_word_count_long_question(self):
        assert _word_count_for_expansion(
            "What is the difference between a list and a tuple?"
        ) == 10


class TestQueryExpansionIntegration:
    """Verify the suffix reaches embed_query and that original is preserved."""

    @pytest.fixture(autouse=True)
    def patch_settings(self):
        with patch("app.services.retrieval.get_settings", return_value=_WITH_KEYS_SETTINGS):
            with patch("app.services.qdrant_service.get_settings", return_value=_WITH_KEYS_SETTINGS):
                yield

    @pytest.mark.asyncio
    async def test_short_query_embeds_with_suffix(self):
        """embed_query must be called with the expanded text for a short query."""
        captured_texts: list[str] = []

        async def fake_embed(text: str, **kwargs):
            captured_texts.append(text)
            return _unit_vec()

        with patch("app.services.retrieval.emb_service.embed_query",
                   side_effect=fake_embed), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=[]):
            await retrieve("what is float")

        assert len(captured_texts) == 1
        assert SHORT_QUERY_SUFFIX in captured_texts[0]
        assert "what is float" in captured_texts[0]

    @pytest.mark.asyncio
    async def test_long_query_embeds_without_suffix(self):
        """embed_query must be called with the exact question for a long query."""
        captured_texts: list[str] = []

        async def fake_embed(text: str, **kwargs):
            captured_texts.append(text)
            return _unit_vec()

        long_q = "What is the difference between supervised and unsupervised learning?"
        with patch("app.services.retrieval.emb_service.embed_query",
                   side_effect=fake_embed), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=[]):
            await retrieve(long_q)

        assert len(captured_texts) == 1
        assert captured_texts[0] == long_q
        assert SHORT_QUERY_SUFFIX not in captured_texts[0]

    @pytest.mark.asyncio
    async def test_original_question_stored_on_result(self):
        """RetrievalResult.original_question must be the user's question, no suffix."""
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=[]):
            result = await retrieve("what is float")

        assert result.original_question == "what is float"
        assert SHORT_QUERY_SUFFIX not in result.original_question

    @pytest.mark.asyncio
    async def test_search_text_has_suffix_on_result(self):
        """RetrievalResult.search_text must carry the expanded text."""
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=[]):
            result = await retrieve("what is float")

        assert SHORT_QUERY_SUFFIX in result.search_text

    @pytest.mark.asyncio
    async def test_trailing_question_mark_still_expands(self):
        """'what is float?' (with ?) must expand the same as 'what is float'."""
        captured_texts: list[str] = []

        async def fake_embed(text: str, **kwargs):
            captured_texts.append(text)
            return _unit_vec()

        with patch("app.services.retrieval.emb_service.embed_query",
                   side_effect=fake_embed), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=[]):
            await retrieve("what is float?")

        assert SHORT_QUERY_SUFFIX in captured_texts[0]

    @pytest.mark.asyncio
    async def test_threshold_unchanged_by_expansion(self):
        """Score threshold must not change due to query expansion."""
        hits = [
            _make_scored_point(0.4, _make_payload()),   # below threshold=0.5
        ]
        with patch("app.services.retrieval.emb_service.embed_query",
                   new_callable=AsyncMock, return_value=_unit_vec()), \
             patch("app.services.retrieval.qdrant_service.search_similar",
                   new_callable=AsyncMock, return_value=hits):
            result = await retrieve("what is float")

        # threshold is 0.5, score is 0.4 → should still fail Gate 1
        assert result.has_evidence is False


class TestRagServiceUsesOriginalQuestion:
    """rag_service must pass original_question (no suffix) to generation."""

    @pytest.fixture(autouse=True)
    def patch_settings(self):
        from app.config import Settings
        settings = Settings(
            _env_file=None,  # type: ignore[call-arg]
            google_api_key="fake-key",
            qdrant_url="https://fake.qdrant.io",
            qdrant_api_key="fake-qdrant-key",
            rag_top_k=5,
            rag_score_threshold=0.5,
            generation_model="gemini-3.5-flash-lite",
            embedding_model="gemini-embedding-001",
            embedding_dimension=3072,
        )
        with patch("app.services.rag_service.get_settings", return_value=settings):
            yield

    @pytest.mark.asyncio
    async def test_generation_prompt_uses_original_question_not_suffix(self):
        """The generation prompt must contain the original question, not the expanded one."""
        import json
        from unittest.mock import MagicMock
        from app.services.rag_service import _GenerationResponse, answer
        from app.services.retrieval import RetrievalResult
        from app.schemas import Source

        original = "what is float"
        search   = f"what is float {SHORT_QUERY_SUFFIX}"

        src = Source(title="Variables", section="Float", path="/m01/vars", score=0.8)
        retrieval = RetrievalResult(
            sources=[src],
            passages=["A float is a decimal number."],
            original_question=original,
            search_text=search,
            top_score=0.8,
            all_candidates_count=1,
            kept_count=1,
        )

        gen = _GenerationResponse(supported=True, answer="A float is a decimal.", used_chunks=[0])
        mock_response = MagicMock()
        mock_response.parsed = gen
        mock_response.text = json.dumps({"supported": True, "answer": "A float is a decimal.", "used_chunks": [0]})

        captured_prompts: list[str] = []

        async def fake_generate(model, contents, config):
            captured_prompts.append(contents)
            return mock_response

        with patch("app.services.rag_service.retrieve",
                   new_callable=AsyncMock, return_value=retrieval), \
             patch("app.services.rag_service._get_client") as mock_c:
            mock_c.return_value.aio.models.generate_content = fake_generate
            await answer("what is float")

        assert len(captured_prompts) == 1
        prompt_text = captured_prompts[0]
        # Prompt must contain the original question
        assert original in prompt_text
        # Prompt must NOT contain the suffix
        assert SHORT_QUERY_SUFFIX not in prompt_text
