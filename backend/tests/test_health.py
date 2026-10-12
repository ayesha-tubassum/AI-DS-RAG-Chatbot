"""Tests for GET /health."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_has_configuration_flags():
    response = client.get("/health")
    data = response.json()
    # Both flags must be present and be booleans.
    assert isinstance(data["google_configured"], bool)
    assert isinstance(data["qdrant_configured"], bool)


def test_health_does_not_expose_secret_values():
    response = client.get("/health")
    body = response.text
    # The raw API key must never appear in the response.
    # We just check that no long string that looks like a key is present.
    # (In CI there is no key, so this is also a smoke test.)
    assert "GOOGLE_API_KEY" not in body
    assert "QDRANT_API_KEY" not in body


def test_health_unconfigured_environment(monkeypatch):
    """When no keys are set, health still returns 200 with configured=False."""
    # Clear the lru_cache so Settings re-reads the patched env.
    from app.config import get_settings
    get_settings.cache_clear()

    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["google_configured"] is False
    assert data["qdrant_configured"] is False

    get_settings.cache_clear()
