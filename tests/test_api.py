"""
Tests for the /api/wizard/chat endpoint HTTP contract.

Covers:
- Property 9: Whitespace-only messages rejected with HTTP 422
- Unit tests: ConnectionError → 503, TimeoutError → 504, FileNotFoundError → 503
"""

# Feature: wizard-local-llm-migration

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# App fixture — patch the LLM singleton before importing the app so the
# test suite doesn't require a running Ollama daemon.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = (
        "RECOMENDAÇÃO: n8n\nJustificativa: Automação de fluxo simples."
    )
    with patch("api.rag._llm_client", mock_llm):
        from api.main import app
        with TestClient(app) as c:
            yield c


# ---------------------------------------------------------------------------
# Property 9: Whitespace-only messages are rejected with HTTP 422
# Validates: Requirements 6.2
# ---------------------------------------------------------------------------

@given(
    message=st.text(
        alphabet=st.characters(whitelist_categories=("Zs",)),
        min_size=1,
    )
)
@settings(max_examples=25, deadline=None)
def test_whitespace_only_message_returns_422(message):
    """Property 9: Whitespace-only messages are rejected with HTTP 422"""
    # Feature: wizard-local-llm-migration, Property 9: whitespace → HTTP 422
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "RECOMENDAÇÃO: n8n\nJustificativa: ok."
    with patch("api.rag._llm_client", mock_llm):
        from api.main import app
        with TestClient(app) as c:
            response = c.post("/api/wizard/chat", json={"message": message})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Unit tests: HTTP error mapping
# Validates: Requirements 6.3, 6.4, 6.5
# ---------------------------------------------------------------------------

def test_connection_error_returns_503(client):
    """ConnectionError from LLM client → HTTP 503 with Portuguese message."""
    with patch("api.rag._llm_client") as mock_llm:
        mock_llm.generate.side_effect = ConnectionError("Ollama unreachable")
        response = client.post("/api/wizard/chat", json={"message": "Preciso de automação"})
    assert response.status_code == 503
    assert "LLM" in response.json()["detail"] or "Ollama" in response.json()["detail"]


def test_timeout_error_returns_504(client):
    """TimeoutError from LLM client → HTTP 504."""
    with patch("api.rag._llm_client") as mock_llm:
        mock_llm.generate.side_effect = TimeoutError("Request timed out")
        response = client.post("/api/wizard/chat", json={"message": "Preciso de automação"})
    assert response.status_code == 504


def test_file_not_found_error_returns_503(client):
    """FileNotFoundError (missing LLAMA_MODEL_PATH) → HTTP 503."""
    with patch("api.rag._llm_client") as mock_llm:
        mock_llm.generate.side_effect = FileNotFoundError("LLAMA_MODEL_PATH not set")
        response = client.post("/api/wizard/chat", json={"message": "Preciso de automação"})
    assert response.status_code == 503
    assert "LLAMA_MODEL_PATH" in response.json()["detail"] or "LLM" in response.json()["detail"]


def test_empty_string_returns_422(client):
    """Empty string message → HTTP 422 (Pydantic min_length=1)."""
    response = client.post("/api/wizard/chat", json={"message": ""})
    assert response.status_code == 422


def test_valid_message_returns_200(client):
    """Valid message → HTTP 200 with WizardResponse."""
    response = client.post("/api/wizard/chat", json={"message": "Preciso de automação de relatórios"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
