# Implementation Plan: contract-fields-update

## Overview

Additive end-to-end propagation of two new optional financial fields (`cost` and `projected_return`) through the Nexus stack: Pydantic model → parser/serializer → SQLite schema + migration → ingestion engine → sample data.

## Tasks

- [x] 1. Update the `ContractCreate` Pydantic model
  - Add `cost: Optional[str] = None` and `projected_return: Optional[str] = None` to `ContractCreate` in `api/models.py`, placed after `docs_link`
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ]* 1.1 Write property test for model accepting new optional fields
    - **Property 1: Model accepts new optional fields**
    - **Validates: Requirements 1.1, 1.2, 1.4**
    - Use `@given(cost=st.one_of(st.none(), st.text()), projected_return=st.one_of(st.none(), st.text()))` in `tests/test_contract_fields.py`

- [x] 2. Update the contract parser and serializer
  - [x] 2.1 Update `parse_contract()` in `api/contract_parser.py`
    - Add `cost=info_fields.get("cost (cloud)")` and `projected_return=info_fields.get("projected_return")` to the `ContractCreate(...)` construction call
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 2.2 Write property test for parser extracting new info fields
    - **Property 2: Parser extracts new info fields**
    - **Validates: Requirements 2.1, 2.2**
    - Use `@given(cost=st.text(min_size=1), projected_return=st.text(min_size=1))` — build a minimal contract text string with those values and assert `parse_contract()` returns matching fields

  - [x] 2.3 Update `serialize_contract()` in `api/contract_parser.py`
    - Append `cost (cloud):` and `projected_return:` lines to the `info:` block (after `docs_link`), guarded by `if contract.cost is not None` / `if contract.projected_return is not None`
    - _Requirements: 2.4_

  - [ ]* 2.4 Write property test for serialize/parse round-trip
    - **Property 3: Serialize/parse round-trip preserves new fields**
    - **Validates: Requirements 2.4, 2.5**
    - Use `@given` with `st.builds(ContractCreate, cost=st.text(min_size=1), projected_return=st.text(min_size=1), ...)` and assert `parse_contract(serialize_contract(c)).cost == c.cost` and same for `projected_return`

- [x] 3. Checkpoint — ensure model and parser tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update the SQLite schema and add migration
  - [x] 4.1 Add new columns to `CREATE TABLE IF NOT EXISTS contracts` in `api/database.py`
    - Append `cost TEXT,` and `projected_return TEXT,` as nullable columns
    - _Requirements: 3.1, 3.2_

  - [x] 4.2 Implement `_migrate_tables()` in `api/database.py`
    - Use `PRAGMA table_info(contracts)` to detect missing columns and run `ALTER TABLE contracts ADD COLUMN cost TEXT` / `ALTER TABLE contracts ADD COLUMN projected_return TEXT` if absent
    - Call `_migrate_tables(conn)` from `create_tables()` after the `CREATE TABLE` statement
    - _Requirements: 3.1, 3.2_

- [x] 5. Update the ingestion engine
  - [x] 5.1 Extend `_upsert_contract()` in `api/ingestion.py`
    - Add `cost` and `projected_return` to both the `INSERT INTO contracts (...)` column list and the `UPDATE contracts SET ...` clause
    - Extend the corresponding parameter tuples with `contract.cost` and `contract.projected_return`
    - _Requirements: 3.3, 3.4, 4.1, 4.2, 4.3_

  - [ ]* 5.2 Write property test for upsert persisting new fields
    - **Property 4: Upsert persists new fields**
    - **Validates: Requirements 3.3, 3.4, 4.1, 4.2**
    - Use `@given` with `st.builds(ContractCreate, cost=st.one_of(st.none(), st.text()), projected_return=st.one_of(st.none(), st.text()), ...)` against an in-memory SQLite DB; assert both insert and update paths store the correct values

- [x] 6. Update sample data files
  - [x] 6.1 Add `cost` and `projected_return` to every record in `data/samples/contracts_catalog.json`
    - Use realistic Brazilian currency strings (e.g., `"R$18.000,00/mês"`, `"a ser estimado"`)
    - _Requirements: 5.1_

  - [x] 6.2 Add `cost (cloud):` and `projected_return:` lines to the `info:` section of `data/samples/dataAI_Contract_ex1.txt`
    - Values must match those already present in the root-level `dataAI_Contract_ex1.txt`
    - _Requirements: 5.2_

  - [ ]* 6.3 Write unit test for sample data ingestion
    - Call `seed_sample_data()` against a fresh in-memory DB and assert `IngestResult` has zero errors and that queried rows contain non-null `cost` / `projected_return` for the updated records
    - _Requirements: 5.3_

- [x] 7. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- All changes are additive and backward-compatible; existing contracts without the new fields default to `NULL`
- Delete `local_db/nexus.db` before running if upgrading an existing database (the migration helper in task 4.2 handles it automatically otherwise)
- Property tests use the **Hypothesis** library; install with `pip install hypothesis` if not already present
