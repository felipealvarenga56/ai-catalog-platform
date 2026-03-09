"""Unit tests for GET /api/reports/executive-dashboard endpoint."""

import json
import os
import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.database import get_connection, create_tables, DB_PATH
from api.ingestion import ingest_file
from api.routes.reports import router as reports_router


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
def client():
    app = FastAPI()
    app.include_router(reports_router)
    return TestClient(app)


def _insert_contracts(contracts: list[dict]):
    """Insert contracts via ingestion from a temp JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(contracts, f)
        path = f.name
    ingest_file(path)
    os.unlink(path)


SAMPLE_CONTRACTS = [
    {
        "business_map_id": "DASH-001", "title": "Automação Workflow",
        "area": "Operações", "initiative": "wide-n8n", "description": "Automação",
        "owner": "Ana", "status": "active", "sec_approval": "approved", "docs_link": "http://docs/1",
    },
    {
        "business_map_id": "DASH-002", "title": "Dashboard BI",
        "area": "Financeiro", "initiative": "BI", "description": "Painel",
        "owner": "Bob", "status": "development",
    },
    {
        "business_map_id": "DASH-003", "title": "Modelo ML",
        "area": "Operações", "initiative": "Deep", "description": "Modelo",
        "owner": "Ana", "status": "active", "sec_approval": "approved",
    },
    {
        "business_map_id": "DASH-004", "title": "Portal Lovable",
        "area": "Financeiro", "initiative": "wide-lovable", "description": "Portal",
        "owner": "Carlos", "status": "staging", "docs_link": "http://docs/4",
    },
]


# --- Empty database ---

def test_empty_db_returns_zeros(client):
    resp = client.get("/api/reports/executive-dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_contracts"] == 0
    assert data["by_status"] == {}
    assert data["by_initiative"] == {}
    assert data["by_area"] == {}
    assert data["by_owner"] == {}
    assert data["compliance"]["sec_approval_count"] == 0
    assert data["compliance"]["sec_approval_percentage"] == 0.0
    assert data["compliance"]["docs_link_count"] == 0
    assert data["compliance"]["docs_link_percentage"] == 0.0
    assert data["cross_area_initiative"] == []
    assert data["cross_area_status"] == []
    assert data["filter_options"]["areas"] == []


# --- Basic aggregations ---

def test_total_and_grouped_counts(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_contracts"] == 4
    assert sum(data["by_status"].values()) == 4
    assert sum(data["by_initiative"].values()) == 4
    assert sum(data["by_area"].values()) == 4
    assert sum(data["by_owner"].values()) == 4

    # Specific group counts
    assert data["by_status"]["active"] == 2
    assert data["by_status"]["development"] == 1
    assert data["by_area"]["Operações"] == 2
    assert data["by_area"]["Financeiro"] == 2
    assert data["by_owner"]["Ana"] == 2


# --- Compliance metrics ---

def test_compliance_metrics(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard")
    data = resp.json()

    # 2 out of 4 have sec_approval
    assert data["compliance"]["sec_approval_count"] == 2
    assert data["compliance"]["sec_approval_percentage"] == 50.0
    # 2 out of 4 have docs_link
    assert data["compliance"]["docs_link_count"] == 2
    assert data["compliance"]["docs_link_percentage"] == 50.0


# --- Cross-tabulations ---

def test_cross_tabulations(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard")
    data = resp.json()

    # Area × Initiative: Operações has wide-n8n(1) and Deep(1), Financeiro has BI(1) and wide-lovable(1)
    cross_ai = {(e["row"], e["col"]): e["count"] for e in data["cross_area_initiative"]}
    assert cross_ai[("Operações", "wide-n8n")] == 1
    assert cross_ai[("Operações", "Deep")] == 1
    assert cross_ai[("Financeiro", "BI")] == 1
    assert cross_ai[("Financeiro", "wide-lovable")] == 1
    assert sum(cross_ai.values()) == 4

    # Area × Status
    cross_as = {(e["row"], e["col"]): e["count"] for e in data["cross_area_status"]}
    assert cross_as[("Operações", "active")] == 2
    assert cross_as[("Financeiro", "development")] == 1
    assert cross_as[("Financeiro", "staging")] == 1


# --- Filter options (always unfiltered) ---

def test_filter_options_always_unfiltered(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    # Even when filtering by area, filter_options should show ALL distinct values
    resp = client.get("/api/reports/executive-dashboard", params={"area": "Operações"})
    data = resp.json()

    assert "Financeiro" in data["filter_options"]["areas"]
    assert "Operações" in data["filter_options"]["areas"]
    assert len(data["filter_options"]["initiatives"]) == 4


# --- Filtering ---

def test_filter_by_area(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard", params={"area": "Operações"})
    data = resp.json()

    assert data["total_contracts"] == 2
    assert "Financeiro" not in data["by_area"]
    assert data["by_area"]["Operações"] == 2


def test_filter_by_status(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard", params={"status": "active"})
    data = resp.json()

    assert data["total_contracts"] == 2
    assert list(data["by_status"].keys()) == ["active"]


def test_filter_no_match_returns_zeros(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard", params={"area": "NonExistent"})
    data = resp.json()

    assert data["total_contracts"] == 0
    assert data["by_status"] == {}
    assert data["compliance"]["sec_approval_percentage"] == 0.0
    assert data["cross_area_initiative"] == []


def test_multiple_filters(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard", params={"area": "Operações", "owner": "Ana"})
    data = resp.json()

    assert data["total_contracts"] == 2
    assert data["by_owner"] == {"Ana": 2}


# --- Response schema validation ---

def test_response_schema_keys(client):
    _insert_contracts(SAMPLE_CONTRACTS)
    resp = client.get("/api/reports/executive-dashboard")
    data = resp.json()

    expected_keys = {
        "total_contracts", "by_status", "by_initiative", "by_area", "by_owner",
        "compliance", "cross_area_initiative", "cross_area_status", "filter_options",
    }
    assert set(data.keys()) == expected_keys

    compliance_keys = {"sec_approval_count", "sec_approval_percentage", "docs_link_count", "docs_link_percentage"}
    assert set(data["compliance"].keys()) == compliance_keys

    filter_keys = {"areas", "initiatives", "statuses", "owners"}
    assert set(data["filter_options"].keys()) == filter_keys
