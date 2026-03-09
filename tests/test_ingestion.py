"""Unit tests for the ingestion engine (api/ingestion.py).

Covers tasks 5.1, 5.2, and 5.3:
- .txt file ingestion via parse_contract()
- .json file ingestion with ContractCreate validation
- IngestResult count invariant (processed = inserted + updated + errored)
"""

import json
import os
import tempfile

import pytest

from api.database import get_connection, create_tables
from api.ingestion import ingest_file, _upsert_contract
from api.models import ContractCreate, ContractInitiative, ContractStatus, IngestResult


@pytest.fixture(autouse=True)
def _fresh_db(tmp_path, monkeypatch):
    """Point the database at a temp directory and create fresh tables for each test."""
    import api.database as db_mod
    db_dir = str(tmp_path)
    db_path = os.path.join(db_dir, "nexus.db")
    monkeypatch.setattr(db_mod, "DB_DIR", db_dir)
    monkeypatch.setattr(db_mod, "DB_PATH", db_path)
    create_tables()


VALID_TXT = """\
dataAI_Contract
id: 100 (businessMap)
info:
  title: Test Project
  area: Engineering
  initiative: Deep
  version: 1.0.0
  description: A test project for unit testing.
  owner: Test Owner
  status: active
  contact:
    name: Alice
    email: alice@example.com

terms:
  usage: Internal use only.
  limitations: None known.
"""

VALID_CONTRACT_DICT = {
    "business_map_id": "200",
    "title": "JSON Contract",
    "area": "Data Science",
    "initiative": "BI",
    "version": "2.0.0",
    "description": "Loaded from JSON.",
    "owner": "Bob",
    "status": "development",
}


# ---------------------------------------------------------------------------
# 5.1 — .txt file ingestion
# ---------------------------------------------------------------------------

class TestTxtIngestion:
    def test_valid_txt_inserts_contract(self, tmp_path):
        txt_file = tmp_path / "contract.txt"
        txt_file.write_text(VALID_TXT, encoding="utf-8")

        result = ingest_file(str(txt_file))

        assert result.total_inserted == 1
        assert result.total_updated == 0
        assert result.errors == []
        assert result.total_processed == 1

        conn = get_connection()
        row = conn.execute("SELECT * FROM contracts WHERE business_map_id = '100'").fetchone()
        conn.close()
        assert row is not None
        assert row["title"] == "Test Project"
        assert row["initiative"] == "Deep"

    def test_txt_upsert_updates_existing(self, tmp_path):
        txt_file = tmp_path / "contract.txt"
        txt_file.write_text(VALID_TXT, encoding="utf-8")

        # First ingestion — insert
        ingest_file(str(txt_file))

        # Second ingestion — update
        result = ingest_file(str(txt_file))
        assert result.total_inserted == 0
        assert result.total_updated == 1
        assert result.total_processed == 1

        # Only one row in the table
        conn = get_connection()
        count = conn.execute("SELECT COUNT(*) as cnt FROM contracts").fetchone()["cnt"]
        conn.close()
        assert count == 1

    def test_txt_missing_header_returns_error(self, tmp_path):
        txt_file = tmp_path / "bad.txt"
        txt_file.write_text("not a contract\nsome content", encoding="utf-8")

        result = ingest_file(str(txt_file))
        assert result.total_inserted == 0
        assert len(result.errors) == 1
        assert "header" in result.errors[0].lower()
        # Count invariant still holds
        assert result.total_processed == result.total_inserted + result.total_updated + len(result.errors)

    def test_txt_missing_required_fields_returns_error(self, tmp_path):
        bad_txt = "dataAI_Contract\nid: 999 (businessMap)\ninfo:\n  title: Only Title\n"
        txt_file = tmp_path / "incomplete.txt"
        txt_file.write_text(bad_txt, encoding="utf-8")

        result = ingest_file(str(txt_file))
        assert result.total_inserted == 0
        assert len(result.errors) == 1


# ---------------------------------------------------------------------------
# 5.2 — .json file ingestion
# ---------------------------------------------------------------------------

class TestJsonIngestion:
    def test_valid_json_inserts_contracts(self, tmp_path):
        records = [VALID_CONTRACT_DICT]
        json_file = tmp_path / "contracts.json"
        json_file.write_text(json.dumps(records), encoding="utf-8")

        result = ingest_file(str(json_file))

        assert result.total_inserted == 1
        assert result.total_updated == 0
        assert result.errors == []
        assert result.total_processed == 1

    def test_json_upsert_by_business_map_id(self, tmp_path):
        records = [VALID_CONTRACT_DICT]
        json_file = tmp_path / "contracts.json"
        json_file.write_text(json.dumps(records), encoding="utf-8")

        ingest_file(str(json_file))
        result = ingest_file(str(json_file))

        assert result.total_inserted == 0
        assert result.total_updated == 1

        conn = get_connection()
        count = conn.execute("SELECT COUNT(*) as cnt FROM contracts").fetchone()["cnt"]
        conn.close()
        assert count == 1

    def test_json_skips_invalid_records(self, tmp_path):
        records = [
            VALID_CONTRACT_DICT,
            {"title": "Missing fields"},  # invalid — missing required fields
        ]
        json_file = tmp_path / "mixed.json"
        json_file.write_text(json.dumps(records), encoding="utf-8")

        result = ingest_file(str(json_file))

        assert result.total_inserted == 1
        assert len(result.errors) == 1
        assert "validation error" in result.errors[0].lower()

    def test_json_not_a_list_returns_error(self, tmp_path):
        json_file = tmp_path / "bad.json"
        json_file.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

        result = ingest_file(str(json_file))
        assert result.total_processed == 0
        assert len(result.errors) == 1
        assert "list" in result.errors[0].lower()

    def test_json_enum_values_stored_correctly(self, tmp_path):
        records = [VALID_CONTRACT_DICT]
        json_file = tmp_path / "contracts.json"
        json_file.write_text(json.dumps(records), encoding="utf-8")

        ingest_file(str(json_file))

        conn = get_connection()
        row = conn.execute("SELECT * FROM contracts WHERE business_map_id = '200'").fetchone()
        conn.close()
        assert row["initiative"] == "BI"
        assert row["status"] == "development"


# ---------------------------------------------------------------------------
# 5.3 — IngestResult count invariant
# ---------------------------------------------------------------------------

class TestIngestResultCounts:
    def test_processed_equals_inserted_plus_updated_plus_errors(self, tmp_path):
        """processed = inserted + updated + len(errors)"""
        records = [
            VALID_CONTRACT_DICT,
            {**VALID_CONTRACT_DICT, "business_map_id": "201"},
            {"bad": "record"},
        ]
        json_file = tmp_path / "mixed.json"
        json_file.write_text(json.dumps(records), encoding="utf-8")

        result = ingest_file(str(json_file))
        assert result.total_processed == result.total_inserted + result.total_updated + len(result.errors)

    def test_count_invariant_on_txt(self, tmp_path):
        txt_file = tmp_path / "contract.txt"
        txt_file.write_text(VALID_TXT, encoding="utf-8")

        result = ingest_file(str(txt_file))
        assert result.total_processed == result.total_inserted + result.total_updated + len(result.errors)

    def test_count_invariant_on_error(self, tmp_path):
        txt_file = tmp_path / "bad.txt"
        txt_file.write_text("not a contract", encoding="utf-8")

        result = ingest_file(str(txt_file))
        assert result.total_processed == result.total_inserted + result.total_updated + len(result.errors)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_unsupported_extension(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("a,b,c", encoding="utf-8")

        result = ingest_file(str(csv_file))
        assert result.total_processed == 0
        assert len(result.errors) == 1
        assert "unsupported" in result.errors[0].lower()

    def test_multiple_contracts_in_json(self, tmp_path):
        records = [
            {**VALID_CONTRACT_DICT, "business_map_id": f"id_{i}"}
            for i in range(5)
        ]
        json_file = tmp_path / "batch.json"
        json_file.write_text(json.dumps(records), encoding="utf-8")

        result = ingest_file(str(json_file))
        assert result.total_inserted == 5
        assert result.total_processed == 5

        conn = get_connection()
        count = conn.execute("SELECT COUNT(*) as cnt FROM contracts").fetchone()["cnt"]
        conn.close()
        assert count == 5
