"""Ingestion engine for the Aura Catalog.

Handles .txt (dataAI_Contract format) and .json (list of contract dicts) files.
Upserts contracts into the SQLite contracts table by business_map_id.
"""

import json
import logging
import os
from pydantic import ValidationError

from api.contract_parser import parse_contract
from api.database import get_connection
from api.models import ContractCreate, IngestResult

logger = logging.getLogger(__name__)


def _upsert_contract(conn, contract: ContractCreate) -> str:
    """Upsert a single contract into the contracts table by business_map_id.

    Returns 'inserted' or 'updated'.
    """
    existing = conn.execute(
        "SELECT id FROM contracts WHERE business_map_id = ?",
        (contract.business_map_id,)
    ).fetchone()

    if existing:
        conn.execute("""
            UPDATE contracts
            SET title = ?, area = ?, initiative = ?, version = ?,
                description = ?, owner = ?, status = ?,
                contact_name = ?, contact_email = ?, sec_approval = ?,
                docs_link = ?, cost = ?, projected_return = ?, usage = ?, limitations = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE business_map_id = ?
        """, (
            contract.title,
            contract.area,
            contract.initiative.value,
            contract.version,
            contract.description,
            contract.owner,
            contract.status.value,
            contract.contact_name,
            contract.contact_email,
            contract.sec_approval,
            contract.docs_link,
            contract.cost,
            contract.projected_return,
            contract.usage,
            contract.limitations,
            contract.business_map_id,
        ))
        return "updated"
    else:
        conn.execute("""
            INSERT INTO contracts (
                business_map_id, title, area, initiative, version,
                description, owner, status, contact_name, contact_email,
                sec_approval, docs_link, cost, projected_return, usage, limitations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contract.business_map_id,
            contract.title,
            contract.area,
            contract.initiative.value,
            contract.version,
            contract.description,
            contract.owner,
            contract.status.value,
            contract.contact_name,
            contract.contact_email,
            contract.sec_approval,
            contract.docs_link,
            contract.cost,
            contract.projected_return,
            contract.usage,
            contract.limitations,
        ))
        return "inserted"


def _ingest_txt(file_path: str) -> IngestResult:
    """Ingest a .txt file in dataAI_Contract format.

    Reads the file, checks for the dataAI_Contract header, parses it,
    and upserts the single contract by business_map_id.
    """
    total_inserted = 0
    total_updated = 0
    errors: list[str] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        return IngestResult(
            total_processed=0, total_inserted=0, total_updated=0,
            errors=[f"Error reading file: {e}"],
        )

    # Quick check for the header before full parsing
    first_line = text.lstrip().split("\n", 1)[0].strip()
    if first_line != "dataAI_Contract":
        return IngestResult(
            total_processed=1, total_inserted=0, total_updated=0,
            errors=[f"File does not contain dataAI_Contract header: {file_path}"],
        )

    conn = get_connection()
    try:
        contract = parse_contract(text)
        action = _upsert_contract(conn, contract)
        if action == "inserted":
            total_inserted = 1
        else:
            total_updated = 1
        conn.commit()
    except (ValueError, ValidationError) as e:
        errors.append(f"Parse/validation error: {e}")
    except Exception as e:
        conn.rollback()
        errors.append(f"Database error: {e}")
    finally:
        conn.close()

    total_processed = total_inserted + total_updated + len(errors)
    return IngestResult(
        total_processed=total_processed,
        total_inserted=total_inserted,
        total_updated=total_updated,
        errors=errors,
    )


def _ingest_json(file_path: str) -> IngestResult:
    """Ingest a .json file containing a list of contract dicts.

    Validates each record through ContractCreate, skips invalid records
    with error logging, and upserts valid ones by business_map_id.
    """
    total_inserted = 0
    total_updated = 0
    errors: list[str] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return IngestResult(
            total_processed=0, total_inserted=0, total_updated=0,
            errors=[f"Error reading JSON file: {e}"],
        )

    if not isinstance(data, list):
        return IngestResult(
            total_processed=0, total_inserted=0, total_updated=0,
            errors=["JSON file must contain a list of objects."],
        )

    conn = get_connection()
    try:
        for i, record in enumerate(data):
            try:
                contract = ContractCreate(**record)
            except (ValidationError, Exception) as e:
                errors.append(f"Record {i}: validation error - {e}")
                logger.warning("Skipping invalid record %d in %s: %s", i, file_path, e)
                continue

            try:
                action = _upsert_contract(conn, contract)
                if action == "inserted":
                    total_inserted += 1
                else:
                    total_updated += 1
            except Exception as e:
                conn.rollback()
                errors.append(f"Record {i}: database error - {e}")

        conn.commit()
    except Exception as e:
        conn.rollback()
        errors.append(f"Database error: {e}")
    finally:
        conn.close()

    total_processed = total_inserted + total_updated + len(errors)
    return IngestResult(
        total_processed=total_processed,
        total_inserted=total_inserted,
        total_updated=total_updated,
        errors=errors,
    )


def ingest_file(file_path: str) -> IngestResult:
    """Main entry point: ingest a .txt or .json file into the contracts table.

    - .txt files: parsed via contract_parser.parse_contract()
    - .json files: validated via ContractCreate Pydantic model
    - Other extensions: returns an error result
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        return _ingest_txt(file_path)
    elif ext == ".json":
        return _ingest_json(file_path)
    else:
        return IngestResult(
            total_processed=0, total_inserted=0, total_updated=0,
            errors=[f"Unsupported file format: {ext}"],
        )


def _seed_delivery_procedures(file_path: str) -> int:
    """Load delivery procedures from a JSON file into SQLite. Returns count inserted/updated."""
    with open(file_path, "r", encoding="utf-8") as f:
        procedures = json.load(f)

    count = 0
    conn = get_connection()
    try:
        for proc in procedures:
            tool_id = proc["tool_id"]
            tool_name = proc["tool_name"]
            steps = json.dumps(proc["steps"], ensure_ascii=False)
            documentation_path = proc.get("documentation_path")
            contact_info = proc.get("contact_info")

            existing = conn.execute(
                "SELECT id FROM delivery_procedures WHERE tool_id = ?", (tool_id,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE delivery_procedures
                    SET tool_name = ?, steps = ?, documentation_path = ?, contact_info = ?
                    WHERE tool_id = ?
                """, (tool_name, steps, documentation_path, contact_info, tool_id))
            else:
                conn.execute("""
                    INSERT INTO delivery_procedures (tool_id, tool_name, steps, documentation_path, contact_info)
                    VALUES (?, ?, ?, ?, ?)
                """, (tool_id, tool_name, steps, documentation_path, contact_info))
            count += 1

        conn.commit()
    finally:
        conn.close()

    return count


def seed_sample_data() -> None:
    """Load all sample data files from data/samples/ into SQLite and ChromaDB.

    Called on FastAPI startup to ensure the PoC has data to demonstrate.
    Skips seeding if contracts already exist in the database.
    """
    from api.rag import index_all_contracts

    # Always re-ingest to pick up any new fields added to sample data
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) as cnt FROM contracts").fetchone()["cnt"]
        if count > 0:
            print(f"[Seed] Database has {count} contracts — re-ingesting to apply any field updates.")
    finally:
        conn.close()

    # Find sample data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(base_dir, "data", "samples")

    if not os.path.isdir(samples_dir):
        print(f"[Seed] Samples directory not found: {samples_dir}")
        return

    # Ingest contract JSON files
    contract_json_files = [
        f for f in os.listdir(samples_dir)
        if f.startswith("contracts_") and f.endswith(".json")
    ]

    # Ingest dataAI_Contract .txt files
    contract_txt_files = [
        f for f in os.listdir(samples_dir)
        if f.startswith("dataAI_Contract_") and f.endswith(".txt")
    ]

    # Combine and process all contract files
    contract_files = sorted(contract_json_files + contract_txt_files)

    total_inserted = 0
    total_errors = 0
    for filename in contract_files:
        file_path = os.path.join(samples_dir, filename)
        result = ingest_file(file_path)
        total_inserted += result.total_inserted + result.total_updated
        total_errors += len(result.errors)
        if result.errors:
            for err in result.errors:
                print(f"[Seed] Error in {filename}: {err}")
        print(f"[Seed] {filename}: {result.total_inserted} inserted, {result.total_updated} updated")

    # Seed delivery procedures
    procedures_file = os.path.join(samples_dir, "delivery_procedures.json")
    if os.path.isfile(procedures_file):
        proc_count = _seed_delivery_procedures(procedures_file)
        print(f"[Seed] {proc_count} delivery procedures loaded.")

    # Index all contracts in ChromaDB for semantic search
    indexed = index_all_contracts()
    print(f"[Seed] ChromaDB indexed with {indexed} contracts.")
    print(f"[Seed] Seed complete: {total_inserted} contracts loaded, {total_errors} errors.")
