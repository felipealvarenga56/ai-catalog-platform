# Requirements Document

## Introduction

The Nexus Governance Platform currently stores project data using a flat, ad-hoc schema with fields like `name`, `description`, `source`, and `estimated_cost`. A new canonical data format — the `dataAI_Contract` — has been defined to standardize how all projects are described across the organization. This feature migrates the platform's data models, database schema, sample data, ingestion engine, and vector store indexing to align with the `dataAI_Contract` template, enabling richer metadata (area, initiative, version, contact info, security approval, documentation links, usage terms) and consistent project governance.

## Glossary

- **Contract**: A standardized project descriptor following the `dataAI_Contract` template format, containing info and terms sections.
- **Initiative**: The development path or tool category for a project (BI, Deep, wide-n8n, wide-lovable, wide-superblocks, Alteryx, Copilot). Replaces the former `source` field.
- **Area**: The stakeholder business area or directorate that owns the project (e.g., Operações de farmácia, pricing ecommerce, jurídico).
- **Ingestion_Engine**: The Python module (`api/ingestion.py`) responsible for reading data files and upserting records into SQLite.
- **Catalog**: The unified project registry stored in SQLite and indexed in ChromaDB for semantic search.
- **Vector_Store**: The ChromaDB collection used for semantic search over project descriptions.
- **Contract_Parser**: The component that reads `dataAI_Contract` text files and converts them into structured Contract objects.
- **Contract_Serializer**: The component that converts structured Contract objects back into the `dataAI_Contract` text format.

## Requirements

### Requirement 1: Contract Data Model

**User Story:** As a developer, I want Pydantic models that reflect the `dataAI_Contract` template fields, so that all project data is validated consistently.

#### Acceptance Criteria

1. THE Contract_Model SHALL define fields for: business_map_id, title, area, initiative, version, description, owner, status, contact_name, contact_email, sec_approval, docs_link, usage, and limitations.
2. WHEN a Contract is created with an initiative value, THE Contract_Model SHALL validate that the initiative is one of: BI, Deep, wide-n8n, wide-lovable, wide-superblocks, Alteryx, Copilot.
3. WHEN a Contract is created with a status value, THE Contract_Model SHALL validate that the status is one of: active, inactive, development, staging.
4. WHEN a Contract is created with missing required fields (title, area, initiative, description), THEN THE Contract_Model SHALL raise a validation error.
5. THE Contract_Model SHALL treat contact_name, contact_email, sec_approval, docs_link, usage, and limitations as optional fields with sensible defaults.

### Requirement 2: Database Schema Migration

**User Story:** As a developer, I want the SQLite schema to store all `dataAI_Contract` fields, so that the full contract metadata is persisted locally.

#### Acceptance Criteria

1. THE Database_Module SHALL create a `contracts` table with columns matching all Contract fields: business_map_id, title, area, initiative, version, description, owner, status, contact_name, contact_email, sec_approval, docs_link, usage, limitations, created_at, updated_at.
2. THE Database_Module SHALL define a unique index on (business_map_id) to prevent duplicate contracts.
3. WHEN the application starts, THE Database_Module SHALL create the `contracts` table if it does not already exist.
4. THE Database_Module SHALL retain the existing `delivery_procedures` table without modification.

### Requirement 3: Contract File Parser and Serializer

**User Story:** As a developer, I want to parse `dataAI_Contract` text files into structured objects and serialize them back, so that the platform can ingest and export contracts in the canonical format.

#### Acceptance Criteria

1. WHEN a valid `dataAI_Contract` text file is provided, THE Contract_Parser SHALL parse it into a Contract object with all fields correctly extracted.
2. WHEN a `dataAI_Contract` text file is missing the `dataAI_Contract` header, THEN THE Contract_Parser SHALL raise a descriptive parse error.
3. WHEN a `dataAI_Contract` text file is missing required fields (title, initiative), THEN THE Contract_Parser SHALL raise a descriptive parse error.
4. THE Contract_Serializer SHALL format a Contract object back into a valid `dataAI_Contract` text representation.
5. FOR ALL valid Contract objects, parsing then serializing then parsing SHALL produce an equivalent Contract object (round-trip property).

### Requirement 4: Ingestion Engine Update

**User Story:** As a developer, I want the ingestion engine to support the new contract format alongside JSON files, so that all sample data can be loaded into the catalog.

#### Acceptance Criteria

1. WHEN a `.txt` file with the `dataAI_Contract` header is provided, THE Ingestion_Engine SHALL parse it using the Contract_Parser and upsert the result into the `contracts` table.
2. WHEN a `.json` file containing a list of contract objects is provided, THE Ingestion_Engine SHALL validate each record against the Contract_Model and upsert into the `contracts` table.
3. WHEN a record fails validation during ingestion, THE Ingestion_Engine SHALL skip the invalid record, log the error, and continue processing remaining records.
4. WHEN upserting a contract, THE Ingestion_Engine SHALL use business_map_id as the deduplication key, updating existing records and inserting new ones.
5. THE Ingestion_Engine SHALL report the count of processed, inserted, updated, and errored records after ingestion completes.

### Requirement 5: Sample Data Conversion

**User Story:** As a developer, I want the existing sample data files converted to the new contract format, so that the PoC demonstrates the canonical data structure.

#### Acceptance Criteria

1. THE Sample_Data SHALL include at least one `.txt` file in `dataAI_Contract` format (the provided example contract).
2. THE Sample_Data SHALL include a JSON file containing multiple contracts converted from the existing `projects_deep.json`, `projects_bi.json`, and `projects_n8n.csv` data.
3. WHEN the seed function runs, THE Ingestion_Engine SHALL load all new-format sample data into the `contracts` table and the Vector_Store.
4. WHEN sample data is loaded, each contract SHALL have a unique business_map_id assigned.

### Requirement 6: ChromaDB Vector Store Update

**User Story:** As a developer, I want the vector store indexing to include the richer contract fields, so that semantic search returns more relevant results.

#### Acceptance Criteria

1. WHEN indexing a contract, THE Vector_Store SHALL build the document text from title, description, area, initiative, owner, and usage fields.
2. WHEN indexing a contract, THE Vector_Store SHALL store initiative, area, status, and business_map_id as metadata for filtering.
3. WHEN querying the catalog, THE Vector_Store SHALL return Contract objects with all fields populated from the `contracts` table.
4. WHEN the seed function completes, THE Vector_Store SHALL contain an index entry for every contract in the `contracts` table.

### Requirement 7: API Endpoint Compatibility

**User Story:** As a developer, I want the project listing and detail API endpoints to serve contract data, so that the frontend and Wizard can access the enriched metadata.

#### Acceptance Criteria

1. THE Projects_API SHALL return contract data using the Contract response model with all `dataAI_Contract` fields.
2. WHEN filtering by initiative, THE Projects_API SHALL accept initiative values matching the Contract_Model initiative enum.
3. WHEN searching by text, THE Projects_API SHALL match against title, description, and area fields.
4. WHEN a contract is requested by ID, THE Projects_API SHALL return the full contract with all fields or a 404 error if not found.
