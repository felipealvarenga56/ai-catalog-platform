# Requirements Document

## Introduction

This feature replaces the Nexus Governance Platform Wizard's local LLM backend (Ollama/Llama-cpp-python) with AWS Bedrock using a Claude Sonnet model. All existing Wizard functionality — RAG pipeline, ChromaDB vector search, prompt augmentation, strategic routing, and the conversational frontend interface — must be preserved. Only the LLM invocation layer changes.

## Glossary

- **Wizard**: Phase II of the Nexus platform; the LLM-powered conversational interface that performs feasibility analysis, strategic routing, catalog information, and gap detection.
- **RAG_Pipeline**: The Retrieval-Augmented Generation pipeline: User Input → Vector Search → Prompt Augmentation → LLM → Structured Response.
- **Bedrock_Client**: The AWS Bedrock boto3 client used to invoke the Claude Sonnet model.
- **Model_ARN**: The AWS Bedrock model identifier `cloude-sonnet-45` (cross-region inference profile ARN) used to invoke Claude Sonnet.
- **ChromaDB**: The local vector store used for semantic search over the Nexus Catalog.
- **ToolSolution**: An enumerated set of recommended delivery paths (Copilot, Lovable, n8n, Alteryx, Equipe Deep, Equipe BI, Squad, No Solution).
- **WizardResponse**: The structured Pydantic response returned by the `/api/wizard/chat` endpoint.
- **Routing_Logic**: The component that maps LLM text output to a `ToolSolution` value.

---

## Requirements

### Requirement 1: Replace Local LLM with AWS Bedrock

**User Story:** As a platform operator, I want the Wizard to call AWS Bedrock instead of a local Ollama instance, so that I can use a managed, high-quality Claude Sonnet model without running local GPU infrastructure.

#### Acceptance Criteria

1. THE `Bedrock_Client` SHALL be initialised using `boto3` with the AWS region and credentials sourced from environment variables (`AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
2. WHEN the Wizard receives a chat message, THE `Bedrock_Client` SHALL invoke the model identified by `Model_ARN` (`cloude-sonnet-45`) via the `bedrock-runtime` service.
3. THE `Bedrock_Client` SHALL send the prompt using the Bedrock `converse` API (or `invoke_model` with the Messages API format) and return the assistant's text response.
4. WHEN the AWS Bedrock call succeeds, THE `RAG_Pipeline` SHALL return the LLM text to the existing routing and response-building logic unchanged.
5. THE system SHALL remove all references to `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `OLLAMA_TIMEOUT` environment variables from `api/rag.py`.

---

### Requirement 2: Preserve RAG Pipeline Integrity

**User Story:** As a Wizard user, I want the semantic search and prompt augmentation steps to remain unchanged, so that my queries are still enriched with relevant catalog context before reaching the LLM.

#### Acceptance Criteria

1. WHEN a chat message is received, THE `RAG_Pipeline` SHALL perform a ChromaDB vector search using `query_catalog` before calling the LLM.
2. THE `RAG_Pipeline` SHALL pass the retrieved `Contract` objects to `build_prompt` to construct the augmented prompt.
3. THE `build_prompt` function SHALL produce a prompt that includes the system persona, available tools list, catalog context block, and the user query — identical in structure to the current implementation.
4. WHEN no similar contracts are found in ChromaDB, THE `RAG_Pipeline` SHALL still call the LLM with a prompt that states no similar contracts were found.

---

### Requirement 3: Preserve Strategic Routing Logic

**User Story:** As a Wizard user, I want the tool recommendation and routing logic to continue working after the LLM swap, so that I still receive a structured `ToolSolution` recommendation.

#### Acceptance Criteria

1. WHEN the LLM returns a response, THE `Routing_Logic` SHALL apply `extract_recommendation` to map the text to a `ToolSolution` value.
2. THE `Routing_Logic` SHALL continue to detect the `RECOMENDAÇÃO: <tool>` pattern as the primary extraction strategy.
3. THE `Routing_Logic` SHALL fall back to keyword scanning when no explicit recommendation pattern is found.
4. WHEN no tool keyword is matched, THE `Routing_Logic` SHALL return `ToolSolution.NO_SOLUTION`.

---

### Requirement 4: Preserve Chat API Contract

**User Story:** As a frontend developer, I want the `/api/wizard/chat` endpoint to behave identically before and after the LLM swap, so that no frontend changes are required.

#### Acceptance Criteria

1. THE `/api/wizard/chat` endpoint SHALL continue to accept a `ChatMessage` body and return a `WizardResponse`.
2. WHEN a whitespace-only message is submitted, THE endpoint SHALL return HTTP 422.
3. WHEN the `Bedrock_Client` raises a `botocore.exceptions.ClientError`, THE endpoint SHALL return HTTP 503 with a descriptive Portuguese error message.
4. WHEN the `Bedrock_Client` raises a `botocore.exceptions.EndpointResolutionError` or connection-level error, THE endpoint SHALL return HTTP 503.
5. WHEN the Bedrock call exceeds the configured timeout, THE endpoint SHALL return HTTP 504.

---

### Requirement 5: Configuration via Environment Variables

**User Story:** As a platform operator, I want all AWS credentials and model settings to be configurable via environment variables, so that I can deploy the platform in different environments without code changes.

#### Acceptance Criteria

1. THE system SHALL read `AWS_REGION` (default: `us-east-1`) from environment variables to configure the `Bedrock_Client`.
2. THE system SHALL read `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from environment variables for authentication.
3. THE system SHALL read `BEDROCK_MODEL_ARN` (default: `cloude-sonnet-45`) from environment variables to allow the model ARN to be overridden without code changes.
4. THE system SHALL read `BEDROCK_TIMEOUT` (default: `60` seconds) from environment variables to configure the Bedrock call timeout.
5. IF any required AWS credential environment variable is missing at startup, THE system SHALL log a warning message indicating which variable is absent.

---

### Requirement 6: Dependency Management

**User Story:** As a developer, I want the project dependencies to reflect the switch from Ollama to AWS Bedrock, so that the environment can be reproduced correctly.

#### Acceptance Criteria

1. THE `requirements.txt` (or equivalent dependency file) SHALL include `boto3` and `botocore` as explicit dependencies.
2. THE `requirements.txt` SHALL remove or mark as optional any Ollama-specific HTTP client dependency that is no longer needed for LLM calls (e.g., `httpx` usage for Ollama).
3. WHERE a `requirements.txt` file exists, THE system SHALL specify minimum compatible version constraints for `boto3` (e.g., `boto3>=1.34.0`).
