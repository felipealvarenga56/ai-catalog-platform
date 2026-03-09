# Implementation Plan: Contract Data Model

## Overview

Migrate the Nexus platform from the flat `projects` schema to the `dataAI_Contract` format. Work proceeds bottom-up: models → parser → database → ingestion → vector store → API → sample data → seed wiring.

## Tasks

- [x] 1. Update Pydantic models in `api/models.py`
  - [x] 1.1 Replace `ProjectSource` with `ContractInitiative` enum (BI, Deep, wide-n8n, wide-lovable, wide-superblocks, Alteryx, Copilot) and `ProjectStatus` with `ContractStatus` enum (active, inactive, development, staging)
    - Remove old `ProjectSource` and `ProjectStatus` enums
    - _Requirements: 1.2, 1.3_
  - [x] 1.2 Replace `ProjectCreate` and `Project` with `ContractCreate` and `Contract` models matching all `dataAI_Contract` fields (business_map_id, title, area, initiative, version, description, owner, status, contact_name, contact_email, sec_approval, docs_link, usage, limitations)
    - Required fields: title, area, initiative, description, owner, business_map_id
    - Optional fields with defaults: contact_name, contact_email, sec_approval, docs_link, usage, limitations
    - Update `WizardResponse.similar_projects` to use `Contract` type
    - _Requirements: 1.1, 1.4, 1.5_
  - [ ]* 1.3 Write property tests for model validation
    - **Property 1: Enum validation rejects invalid values**
    - **Property 2: Required field omission causes validation error**
    - **Validates: Requirements 1.2, 1.3, 1.4**

- [x] 2. Create contract parser and serializer in `api/contract_parser.py`
  - [x] 2.1 Implement `parse_contract(text: str) -> ContractCreate` function
    - Parse `dataAI_Contract` header, `id:` line, `info:` section with nested `contact:`, and `terms:` section
    - Handle multi-line fields using `|` continuation marker
    - Raise `ValueError` for missing header or required fields
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 2.2 Implement `serialize_contract(contract: ContractCreate) -> str` function
    - Output valid `dataAI_Contract` text format with proper indentation
    - Handle multi-line description, usage fields with `|` marker
    - _Requirements: 3.4_
  - [ ]* 2.3 Write property test for parser/serializer round-trip
    - **Property 3: Parser/Serializer round-trip**
    - Create a Hypothesis strategy that generates valid `ContractCreate` objects
    - **Validates: Requirements 3.1, 3.4, 3.5**
  - [ ]* 2.4 Write unit tests for parser edge cases
    - Test parsing the provided `dataAI_Contract_ex1.txt` example
    - Test missing header raises ValueError
    - Test missing required fields raises ValueError
    - _Requirements: 3.2, 3.3_

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update database schema in `api/database.py`
  - [x] 4.1 Replace `projects` table creation with `contracts` table in `create_tables()`
    - Define all columns matching Contract model fields
    - Add UNIQUE constraint on `business_map_id`
    - Keep `delivery_procedures` table unchanged
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ]* 4.2 Write unit tests for database schema
    - Verify `contracts` table is created with correct columns
    - Verify unique index on `business_map_id` prevents duplicates
    - Verify `delivery_procedures` table still exists
    - _Requirements: 2.1, 2.2, 2.4_

- [x] 5. Update ingestion engine in `api/ingestion.py`
  - [x] 5.1 Implement `.txt` file ingestion using `parse_contract()`
    - Detect `dataAI_Contract` header in `.txt` files
    - Parse and upsert single contract by `business_map_id`
    - _Requirements: 4.1_
  - [x] 5.2 Update `.json` file ingestion to validate against `ContractCreate`
    - Validate each dict through `ContractCreate(**record)`
    - Upsert by `business_map_id` instead of `(name, source)`
    - Skip invalid records with error logging
    - _Requirements: 4.2, 4.3_
  - [x] 5.3 Update `IngestResult` reporting to reflect new upsert logic
    - Ensure processed = inserted + updated + errored
    - _Requirements: 4.5_
  - [ ]* 5.4 Write property tests for ingestion
    - **Property 4: Ingestion upsert idempotence**
    - **Property 5: Ingestion count invariant**
    - **Property 6: Invalid records skipped, valid records ingested**
    - **Validates: Requirements 4.3, 4.4, 4.5**

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Convert sample data and update seed
  - [x] 7.1 Create `data/samples/contracts_catalog.json` with all existing projects converted to contract format
    - Assign unique `business_map_id` to each contract
    - Map old `source` values to new `initiative` values (deep→Deep, bi→BI, n8n→wide-n8n)
    - Map old `status` values to new status values (ativo→active, em_desenvolvimento→development, concluido→inactive, pausado→inactive)
    - _Requirements: 5.2, 5.4_
  - [x] 7.2 Copy `dataAI_Contract_ex1.txt` to `data/samples/` as a sample `.txt` contract
    - _Requirements: 5.1_
  - [x] 7.3 Update `seed_sample_data()` to load new contract files
    - Look for `contracts_*.json` and `dataAI_Contract_*.txt` files
    - Remove references to old `projects_*.json` and `projects_*.csv` files
    - Index all contracts in ChromaDB after loading
    - _Requirements: 5.3_

- [x] 8. Update ChromaDB indexing in `api/rag.py`
  - [x] 8.1 Update `index_project()` → `index_contract()` to build richer document text from title, description, area, initiative, owner, usage
    - Store initiative, area, status, business_map_id as metadata
    - Rename collection from `nexus_projects` to `nexus_contracts`
    - _Requirements: 6.1, 6.2_
  - [x] 8.2 Update `index_all_projects()` → `index_all_contracts()` to read from `contracts` table
    - _Requirements: 6.4_
  - [x] 8.3 Update `query_catalog()` to return `Contract` objects from `contracts` table
    - _Requirements: 6.3_
  - [ ]* 8.4 Write property test for indexing completeness
    - **Property 7: Indexing completeness**
    - **Validates: Requirements 6.1, 6.2**

- [x] 9. Update API routes in `api/routes/projects.py`
  - [x] 9.1 Update `_row_to_project()` → `_row_to_contract()` to map all contract columns
    - _Requirements: 7.1_
  - [x] 9.2 Update `list_projects()` to query `contracts` table, rename `source` filter to `initiative`, search against title/description/area
    - _Requirements: 7.2, 7.3_
  - [x] 9.3 Update `get_project()` to query `contracts` table by ID
    - _Requirements: 7.4_
  - [ ]* 9.4 Write property tests for API endpoints
    - **Property 8: API initiative filter returns only matching contracts**
    - **Property 9: API text search matches title, description, and area**
    - **Property 10: API get-by-ID returns correct contract or 404**
    - **Validates: Requirements 7.2, 7.3, 7.4**

- [x] 10. Wire everything together and update remaining references
  - [x] 10.1 Update `api/routing.py` to align `ToolSolution` keywords with new initiative names
    - _Requirements: 7.2_
  - [x] 10.2 Update `api/rag.py` `build_prompt()` to use Contract fields (title, initiative instead of name, source)
    - _Requirements: 6.3_
  - [x] 10.3 Update `api/routes/wizard.py` and `api/routes/reports.py` to use Contract model
    - _Requirements: 7.1_
  - [x] 10.4 Update `api/main.py` startup to call updated `create_tables()` and `seed_sample_data()`
    - _Requirements: 2.3, 5.3_
  - [x] 10.5 Remove old sample data files (`projects_deep.json`, `projects_bi.json`, `projects_n8n.csv`)
    - _Requirements: 5.2_

- [x] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis with minimum 100 iterations per property
- The old `projects` table is fully replaced by `contracts` — no migration path needed since this is a PoC with sample data
- Checkpoints ensure incremental validation at key integration points
