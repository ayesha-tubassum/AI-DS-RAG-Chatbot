"""
Tests for app/services/embeddings.py.

All tests use a mock client — no real API calls are made.
"""

import asyncio
import math
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.config import Settings, get_settings
from app.core.errors import EmbeddingError, NotConfiguredError
from app.services.embeddings import (
    BATCH_SIZE,
    _maybe_normalize,
    embed_documents,
    embed_query,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_client(vectors: list[list[float]]) -> MagicMock:
    """
    Build a mock genai.Client whose aio.models.embed_content returns
    an EmbedContentResponse containing the given vectors.
    """
    # Build fake ContentEmbedding objects
    fake_embeddings = []
    for vec in vectors:
        emb = MagicMock()
        emb.values = vec
        fake_embeddings.append(emb)

    fake_response = MagicMock()
    fake_response.embeddings = fake_embeddings

    mock_client = MagicMock()
    mock_client.aio.models.embed_content = AsyncMock(return_value=fake_response)
    return mock_client


def _unit_vector(n: int) -> list[float]:
    """Return a normalized vector of length n (all values equal)."""
    val = 1.0 / math.sqrt(n)
    return [val] * n


# ---------------------------------------------------------------------------
# _maybe_normalize
# ---------------------------------------------------------------------------

class TestMaybeNormalize:
    def test_3072_unchanged(self):
        """At 3072 dims the API already normalizes; we return the vector as-is."""
        vec = [0.5, 0.3, 0.2] + [0.0] * (3072 - 3)
        result = _maybe_normalize(vec, 3072)
        assert result is vec  # same object, no copy

    def test_768_normalized(self):
        """At 768 dims we normalize; the result should have unit L2 norm."""
        vec = [2.0] * 768
        result = _maybe_normalize(vec, 768)
        norm = math.sqrt(sum(x * x for x in result))
        assert abs(norm - 1.0) < 1e-6

    def test_1536_normalized(self):
        vec = [3.0] * 1536
        result = _maybe_normalize(vec, 1536)
        norm = math.sqrt(sum(x * x for x in result))
        assert abs(norm - 1.0) < 1e-6

    def test_zero_vector_unchanged(self):
        """A zero vector cannot be normalized; we return it unchanged."""
        vec = [0.0] * 768
        result = _maybe_normalize(vec, 768)
        assert all(v == 0.0 for v in result)


# ---------------------------------------------------------------------------
# embed_query
# ---------------------------------------------------------------------------

class TestEmbedQuery:
    @pytest.fixture(autouse=True)
    def clear_settings_cache(self, monkeypatch):
        get_settings.cache_clear()
        monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
        monkeypatch.setenv("EMBEDDING_DIMENSION", "3072")
        monkeypatch.setenv("EMBEDDING_MODEL", "gemini-embedding-001")
        yield
        get_settings.cache_clear()

    @pytest.mark.asyncio
    async def test_returns_correct_length(self):
        vec = _unit_vector(3072)
        mock_client = _make_mock_client([vec])

        result = await embed_query("What is pandas?", client=mock_client)

        assert len(result) == 3072

    @pytest.mark.asyncio
    async def test_calls_with_retrieval_query_task_type(self):
        vec = _unit_vector(3072)
        mock_client = _make_mock_client([vec])

        await embed_query("Hello", client=mock_client)

        call_kwargs = mock_client.aio.models.embed_content.call_args.kwargs
        assert call_kwargs["config"].task_type == "RETRIEVAL_QUERY"

    @pytest.mark.asyncio
    async def test_calls_with_correct_output_dimensionality(self):
        vec = _unit_vector(3072)
        mock_client = _make_mock_client([vec])

        await embed_query("Hello", client=mock_client)

        call_kwargs = mock_client.aio.models.embed_content.call_args.kwargs
        assert call_kwargs["config"].output_dimensionality == 3072

    @pytest.mark.asyncio
    async def test_wrong_length_raises_embedding_error(self):
        """If the API returns a vector of the wrong length, raise EmbeddingError."""
        # Return a 100-dim vector instead of 3072
        wrong_vec = [0.1] * 100
        mock_client = _make_mock_client([wrong_vec])

        with pytest.raises(EmbeddingError, match="Vector length mismatch"):
            await embed_query("Hello", client=mock_client)

    @pytest.mark.asyncio
    async def test_empty_response_raises_embedding_error(self):
        fake_response = MagicMock()
        fake_response.embeddings = []
        mock_client = MagicMock()
        mock_client.aio.models.embed_content = AsyncMock(return_value=fake_response)

        with pytest.raises(EmbeddingError):
            await embed_query("Hello", client=mock_client)

    @pytest.mark.asyncio
    async def test_missing_key_raises_not_configured(self, monkeypatch):
        """When GOOGLE_API_KEY is absent, NotConfiguredError must be raised."""
        # Patch get_settings to return a no-key Settings, bypassing any .env file.
        no_key_settings = Settings(
            _env_file=None,  # type: ignore[call-arg]
            google_api_key=None,
            qdrant_url=None,
            qdrant_api_key=None,
        )
        with patch("app.services.embeddings.get_settings", return_value=no_key_settings):
            with pytest.raises(NotConfiguredError):
                await embed_query("Hello")  # no client injected → checks settings


# ---------------------------------------------------------------------------
# embed_documents
# ---------------------------------------------------------------------------

class TestEmbedDocuments:
    @pytest.fixture(autouse=True)
    def clear_settings_cache(self, monkeypatch):
        get_settings.cache_clear()
        monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
        monkeypatch.setenv("EMBEDDING_DIMENSION", "3072")
        monkeypatch.setenv("EMBEDDING_MODEL", "gemini-embedding-001")
        yield
        get_settings.cache_clear()

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty(self):
        result = await embed_documents([])
        assert result == []

    @pytest.mark.asyncio
    async def test_single_document(self):
        vec = _unit_vector(3072)
        mock_client = _make_mock_client([vec])

        result = await embed_documents(["NumPy is great."], client=mock_client)

        assert len(result) == 1
        assert len(result[0]) == 3072

    @pytest.mark.asyncio
    async def test_multiple_documents(self):
        vecs = [_unit_vector(3072) for _ in range(3)]
        mock_client = _make_mock_client(vecs)

        result = await embed_documents(["a", "b", "c"], client=mock_client)

        assert len(result) == 3
        for v in result:
            assert len(v) == 3072

    @pytest.mark.asyncio
    async def test_uses_retrieval_document_task_type(self):
        vec = _unit_vector(3072)
        mock_client = _make_mock_client([vec])

        await embed_documents(["a passage"], client=mock_client)

        call_kwargs = mock_client.aio.models.embed_content.call_args.kwargs
        assert call_kwargs["config"].task_type == "RETRIEVAL_DOCUMENT"

    @pytest.mark.asyncio
    async def test_batching_splits_large_list(self, monkeypatch):
        """Lists larger than BATCH_SIZE must be split into multiple API calls."""
        total = BATCH_SIZE + 5  # one full batch + a remainder
        texts = [f"doc {i}" for i in range(total)]

        # Each call to embed_content returns the right number of fake vectors.
        call_count = 0

        async def fake_embed_content(*, model, contents, config):
            nonlocal call_count
            call_count += 1
            n = len(contents) if isinstance(contents, list) else 1
            fake_vecs = []
            for _ in range(n):
                emb = MagicMock()
                emb.values = _unit_vector(3072)
                fake_vecs.append(emb)
            resp = MagicMock()
            resp.embeddings = fake_vecs
            return resp

        mock_client = MagicMock()
        mock_client.aio.models.embed_content = AsyncMock(side_effect=fake_embed_content)

        result = await embed_documents(texts, client=mock_client)

        assert len(result) == total
        assert call_count == 2  # ceil(total / BATCH_SIZE) == 2


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------

class TestRetry:
    @pytest.fixture(autouse=True)
    def clear_settings_cache(self, monkeypatch):
        get_settings.cache_clear()
        monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
        monkeypatch.setenv("EMBEDDING_DIMENSION", "3072")
        monkeypatch.setenv("EMBEDDING_MODEL", "gemini-embedding-001")
        yield
        get_settings.cache_clear()

    @pytest.mark.asyncio
    async def test_retries_on_temporary_error_then_succeeds(self, monkeypatch):
        """On the first call raise a 429-style error; second call succeeds."""
        from google.genai.errors import APIError as GeminiAPIError

        vec = _unit_vector(3072)
        success_emb = MagicMock()
        success_emb.values = vec
        success_resp = MagicMock()
        success_resp.embeddings = [success_emb]

        # Simulate a rate-limit error on the first attempt.
        rate_limit_exc = GeminiAPIError(429, None)

        call_count = 0

        async def flaky_embed(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise rate_limit_exc
            return success_resp

        mock_client = MagicMock()
        mock_client.aio.models.embed_content = AsyncMock(side_effect=flaky_embed)

        # Patch asyncio.sleep so the test doesn't actually wait 2 seconds.
        with patch("app.services.embeddings.asyncio.sleep", new_callable=AsyncMock):
            result = await embed_query("test", client=mock_client)

        assert len(result) == 3072
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_exhausted_raises_embedding_error(self, monkeypatch):
        """If every attempt fails, EmbeddingError is raised after all retries."""
        from google.genai.errors import APIError as GeminiAPIError

        rate_limit_exc = GeminiAPIError(429, None)

        mock_client = MagicMock()
        mock_client.aio.models.embed_content = AsyncMock(side_effect=rate_limit_exc)

        with patch("app.services.embeddings.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(EmbeddingError):
                await embed_query("test", client=mock_client)
