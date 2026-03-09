"""Checkpoint 6: Verificação dos módulos Wizard e Entrega.

Validates that the Wizard (RAG pipeline, routing) and Delivery (procedures)
endpoints work correctly.
"""

import os
import json

import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.database import get_connection, create_tables, DB_PATH
from api.ingestion import ingest_file
from api.routing import extract_recommendation, ToolRecommendation
from api.models import ToolSolution
from api.routes.wizard import router as wizard_router
from api.routes.delivery import router as delivery_router


@pytest.fixture(autouse=True)
def clean_db():
    """Use a fresh database for each test."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    create_tables()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


@pytest.fixture
def app():
    _app = FastAPI()
    _app.include_router(wizard_router)
    _app.include_router(delivery_router)
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


def _seed_delivery_procedures():
    """Insert sample delivery procedures for testing."""
    conn = get_connection()
    procedures = [
        ("copilot", "GitHub Copilot", json.dumps(["Abrir ticket", "Solicitar licença"]), None, "ti@empresa.com"),
        ("n8n", "n8n", json.dumps(["Acessar portal", "Criar workflow"]), "data/delivery/n8n_guide.pdf", "deep@empresa.com"),
    ]
    for p in procedures:
        conn.execute(
            "INSERT INTO delivery_procedures (tool_id, tool_name, steps, documentation_path, contact_info) VALUES (?, ?, ?, ?, ?)",
            p,
        )
    conn.commit()
    conn.close()


# =============================================
# Routing Logic Tests
# =============================================

def test_extract_recommendation_copilot():
    """Routing extracts Copilot from explicit recommendation."""
    resp = "RECOMENDAÇÃO: Copilot\nIdeal para geração de código assistida."
    rec = extract_recommendation(resp)
    assert rec.tool == ToolSolution.COPILOT
    assert len(rec.justification) > 0


def test_extract_recommendation_n8n():
    """Routing extracts n8n from keyword in response."""
    resp = "Para automação de workflows, recomendo usar n8n."
    rec = extract_recommendation(resp)
    assert rec.tool == ToolSolution.N8N


def test_extract_recommendation_no_solution():
    """Routing returns NO_SOLUTION when no tool matches."""
    resp = "Esta é uma resposta genérica sem menção a ferramentas."
    rec = extract_recommendation(resp)
    assert rec.tool == ToolSolution.NO_SOLUTION


def test_extract_recommendation_explicit_no_solution():
    """Routing detects explicit 'não temos solução' phrase."""
    resp = "Não temos uma solução disponível hoje para esta demanda."
    rec = extract_recommendation(resp)
    assert rec.tool == ToolSolution.NO_SOLUTION


def test_extract_recommendation_all_tools():
    """Each tool keyword is correctly detected."""
    cases = [
        ("Use o Copilot para isso", ToolSolution.COPILOT),
        ("Lovable é a melhor opção", ToolSolution.LOVABLE),
        ("Recomendo n8n para automação", ToolSolution.N8N),
        ("Alteryx resolve esse caso", ToolSolution.ALTERYX),
        ("Encaminhe para a equipe BI", ToolSolution.BI_TEAM),
        ("A equipe Deep pode ajudar", ToolSolution.DEEP_TEAM),
        ("Isso requer um squad de desenvolvimento", ToolSolution.SQUAD),
    ]
    for text, expected_tool in cases:
        rec = extract_recommendation(text)
        assert rec.tool == expected_tool, f"Failed for: {text}"


# =============================================
# Wizard Endpoint Tests
# =============================================

def test_wizard_rejects_empty_message(client):
    """Wizard rejects empty string with 422."""
    resp = client.post("/api/wizard/chat", json={"message": ""})
    assert resp.status_code == 422


def test_wizard_rejects_whitespace_message(client):
    """Wizard rejects whitespace-only message with 422."""
    resp = client.post("/api/wizard/chat", json={"message": "   \t\n  "})
    assert resp.status_code == 422


@patch("api.rag.query_catalog")
def test_wizard_returns_response(mock_query, client):
    """Wizard returns a valid WizardResponse when LLM is available."""
    mock_query.return_value = []
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "RECOMENDAÇÃO: n8n\nIdeal para automação de processos."
    with patch("api.rag._llm_client", mock_llm):
        resp = client.post("/api/wizard/chat", json={"message": "Preciso automatizar um processo"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["recommended_tool"] == "n8n"
    assert data["justification"] is not None


@patch("api.rag.query_catalog")
def test_wizard_no_solution_response(mock_query, client):
    """Wizard includes 'não temos' message when no tool matches."""
    mock_query.return_value = []
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Não consigo identificar uma ferramenta adequada para isso."
    with patch("api.rag._llm_client", mock_llm):
        resp = client.post("/api/wizard/chat", json={"message": "Quero algo muito específico"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["recommended_tool"] == "no_solution"


@patch("api.rag.query_catalog")
def test_wizard_llm_unavailable_returns_503(mock_query, client):
    """Wizard returns 503 when LLM is unreachable."""
    mock_query.return_value = []
    mock_llm = MagicMock()
    mock_llm.generate.side_effect = ConnectionError("LLM unreachable")
    with patch("api.rag._llm_client", mock_llm):
        resp = client.post("/api/wizard/chat", json={"message": "Olá"})
    assert resp.status_code == 503
    assert "indisponível" in resp.json()["detail"].lower()


@patch("api.rag.query_catalog")
def test_wizard_timeout_returns_504(mock_query, client):
    """Wizard returns 504 when LLM call times out."""
    mock_query.return_value = []
    mock_llm = MagicMock()
    mock_llm.generate.side_effect = TimeoutError("Request timed out")
    with patch("api.rag._llm_client", mock_llm):
        resp = client.post("/api/wizard/chat", json={"message": "Olá"})
    assert resp.status_code == 504
    assert "tempo" in resp.json()["detail"].lower()


# =============================================
# Delivery Endpoint Tests
# =============================================

def test_delivery_list_tools_empty(client):
    """List tools returns empty list when no procedures exist."""
    resp = client.get("/api/delivery/tools")
    assert resp.status_code == 200
    assert resp.json() == []


def test_delivery_list_tools_with_data(client):
    """List tools returns all registered procedures."""
    _seed_delivery_procedures()
    resp = client.get("/api/delivery/tools")
    assert resp.status_code == 200
    tools = resp.json()
    assert len(tools) == 2
    tool_ids = {t["tool_id"] for t in tools}
    assert "copilot" in tool_ids
    assert "n8n" in tool_ids


def test_delivery_get_instructions(client):
    """Get instructions returns procedure for a valid tool_id."""
    _seed_delivery_procedures()
    resp = client.get("/api/delivery/instructions/copilot")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tool_id"] == "copilot"
    assert data["tool_name"] == "GitHub Copilot"
    assert isinstance(data["steps"], list)
    assert len(data["steps"]) > 0


def test_delivery_get_instructions_with_docs(client):
    """Procedure with documentation_path includes it in response."""
    _seed_delivery_procedures()
    resp = client.get("/api/delivery/instructions/n8n")
    assert resp.status_code == 200
    data = resp.json()
    assert data["documentation_path"] is not None
    assert "n8n_guide" in data["documentation_path"]


def test_delivery_fallback_unknown_tool(client):
    """Unknown tool_id returns 404 with fallback message."""
    resp = client.get("/api/delivery/instructions/unknown_tool")
    assert resp.status_code == 404
    assert "elaboração" in resp.json()["detail"].lower()
