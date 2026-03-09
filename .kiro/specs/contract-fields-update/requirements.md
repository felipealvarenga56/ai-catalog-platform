# Requirements Document

## Introduction

The `dataAI_Contract` format has been updated to include two new financial fields: `cost (cloud)` and `projected_return`. These fields capture the monthly cloud infrastructure cost and the projected financial return of each project. The Nexus platform must be updated end-to-end to support these fields — from the contract text format and its parser, through the data model and database schema, to the ingestion pipeline and sample data.

## Glossary

- **Contract**: A `dataAI_Contract` text document or its parsed representation, describing a Nexus project.
- **ContractCreate**: The Pydantic model used to validate and transfer contract data within the backend.
- **Parser**: The `contract_parser.py` module responsible for converting `dataAI_Contract` text into `ContractCreate` objects.
- **Serializer**: The `serialize_contract` function in `contract_parser.py` that converts a `ContractCreate` object back to `dataAI_Contract` text format.
- **Ingestion_Engine**: The `ingestion.py` module responsible for reading contract files and upserting them into the SQLite database.
- **Catalog**: The SQLite `contracts` table that stores all project contracts.
- **cost**: A string field representing the monthly cloud infrastructure cost of a project (e.g., `R$18.000,00/mês`). Optional.
- **projected_return**: A string field representing the estimated financial return of a project (e.g., `R$xx.xxx,xx/mês de receita`, `a ser estimado`). Optional.
- **Sample_Data**: The files under `data/samples/` used to seed the Nexus PoC database on startup.

---

## Requirements

### Requirement 1: Data Model Update

**User Story:** As a developer, I want the `ContractCreate` Pydantic model to include `cost` and `projected_return` fields, so that the application can represent and validate the complete contract structure.

#### Acceptance Criteria

1. THE `ContractCreate` model SHALL include an optional `cost` field of type `str`.
2. THE `ContractCreate` model SHALL include an optional `projected_return` field of type `str`.
3. WHEN a `ContractCreate` object is instantiated without `cost` or `projected_return`, THE model SHALL default both fields to `None`.
4. WHEN a `ContractCreate` object is instantiated with valid string values for `cost` and `projected_return`, THE model SHALL accept and store those values without error.

---

### Requirement 2: Contract Parser Update

**User Story:** As a developer, I want the contract parser to extract `cost` and `projected_return` from `dataAI_Contract` text files, so that ingested contracts carry complete financial information.

#### Acceptance Criteria

1. WHEN a `dataAI_Contract` text contains a `cost (cloud):` field under the `info:` section, THE Parser SHALL extract its value and map it to the `cost` field of the resulting `ContractCreate` object.
2. WHEN a `dataAI_Contract` text contains a `projected_return:` field under the `info:` section, THE Parser SHALL extract its value and map it to the `projected_return` field of the resulting `ContractCreate` object.
3. WHEN a `dataAI_Contract` text does not contain `cost (cloud):` or `projected_return:`, THE Parser SHALL set the corresponding fields to `None` without raising an error.
4. WHEN a `dataAI_Contract` text contains both `cost (cloud):` and `projected_return:`, THE Serializer SHALL include both fields in the serialized output under the `info:` section.
5. FOR ALL valid `ContractCreate` objects with non-null `cost` and `projected_return`, parsing the serialized output SHALL produce a `ContractCreate` object with equivalent `cost` and `projected_return` values (round-trip property).

---

### Requirement 3: Database Schema Update

**User Story:** As a developer, I want the SQLite `contracts` table to store `cost` and `projected_return`, so that the Catalog persists the full financial data of each contract.

#### Acceptance Criteria

1. THE Catalog's `contracts` table SHALL include a `cost` column of type `TEXT`, nullable.
2. THE Catalog's `contracts` table SHALL include a `projected_return` column of type `TEXT`, nullable.
3. WHEN the Ingestion_Engine inserts a new contract, THE Ingestion_Engine SHALL write the `cost` and `projected_return` values to their respective columns.
4. WHEN the Ingestion_Engine updates an existing contract, THE Ingestion_Engine SHALL update the `cost` and `projected_return` columns with the new values.

---

### Requirement 4: Ingestion Engine Update

**User Story:** As a developer, I want the ingestion engine to handle `cost` and `projected_return` when processing both `.txt` and `.json` contract files, so that all ingestion paths persist the new fields correctly.

#### Acceptance Criteria

1. WHEN the Ingestion_Engine processes a `.txt` contract file containing `cost` and `projected_return`, THE Ingestion_Engine SHALL pass those values through to the database upsert.
2. WHEN the Ingestion_Engine processes a `.json` contract file where records include `cost` and `projected_return` keys, THE Ingestion_Engine SHALL validate and persist those values via `ContractCreate`.
3. WHEN the Ingestion_Engine processes a `.json` contract file where records omit `cost` or `projected_return`, THE Ingestion_Engine SHALL accept the record and store `NULL` for the missing fields without raising a validation error.

---

### Requirement 5: Sample Data Update

**User Story:** As a developer, I want the sample data files to include `cost` and `projected_return` values, so that the PoC demonstrates the new fields with realistic data.

#### Acceptance Criteria

1. THE `data/samples/contracts_catalog.json` file SHALL include `cost` and `projected_return` fields for every contract record.
2. THE `data/samples/dataAI_Contract_ex1.txt` file SHALL include `cost (cloud):` and `projected_return:` fields in the `info:` section, consistent with the values already present in the root-level `dataAI_Contract_ex1.txt`.
3. WHEN the Nexus application seeds the database from sample data, THE Ingestion_Engine SHALL successfully ingest all sample contracts including the new fields without errors.
