# Requirements Document

## Introduction

This feature migrates the Aura Governance Platform Wizard's LLM backend from AWS Bedrock back to a local LLM runtime (Ollama as primary, llama-cpp-python as fallback). The migration restores the platform's local-first, zero-API-cost, data-private architecture as mandated by the product specification. All existing Wizard functionality — RAG pipeline, ChromaDB vector search, prompt augmentation, strategic routing, and the conversational frontend interface — must be preserved. Only the LLM invocation layer changes.

## Glossary

- **Wizard**: Phase II of the Aura platform; the LLM-powered conversational interface that performs feasibility analysis, strategic routing, catalog lookup, and gap detection.
- **RAG_Pipeline**: The Retrieval-Augmented Generation pipeline: User Input → Vector Search (ChromaDB) → Prompt Augmentation → Local LLM → Structured Response.
- **Local_LLM_Client**: The component responsible for invoking the locally running LLM (Ollama HTTP API or llama-cpp-python).
- **Ollama**: A local LLM runtime that exposes an OpenAI-compatible HTTP API at `http://localhost:11434`.
- **Llama_cpp**: The `llama-cpp-python` library used as a fallback when Ollama is unavailable.
- **LLM_Backend**: An enumerated configuration value (`ollama` or `llama_cpp`) that selects which local runtime the `Local_LLM_Client` uses.
- **ChromaDB**: The local vector store used for semantic search over the Aura Catalog.
- **ToolSolution**: An enumerated set of recommended delivery paths (Copilot, Lovable, n8n, Alteryx, Equipe Deep, Equipe BI, Squad, No Solution).
- **WizardResponse**: The structured Pydantic response returned by the `/api/wizard/chat` endpoint.
- **Routing_Logic**: The component that maps LLM text output to a `ToolSolution` value.

---

## Requirements

### Requirement 1: Replace AWS Bedrock with Local LLM Client

**User Story:** As a platform operator, I want the Wizard to call a locally running LLM instead of AWS Bedrock, so that the platform runs with zero API costs, no cloud credentials, and full data privacy.

#### Acceptance Criteria

1. THE `Local_LLM_Client` SHALL replace all `boto3` / `botocore` Bedrock invocation code in `api/rag.py`.
2. WHEN `LLM_BACKEND` is set to `ollama` (default), THE `Local_LLM_Client` SHALL send the prompt to the Ollama HTTP API at the URL configured by `OLLAMA_BASE_URL` (default: `http://localhost:11434`).
3. WHEN `LLM_BACKEND` is set to `llama_cpp`, THE `Local_LLM_Client` SHALL load the model file at the path configured by `LLAMA_MODEL_PATH` and invoke it via `llama-cpp-python`.
4. THE system SHALL remove all references to `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ARN`, and `BEDROCK_TIMEOUT` environment variables from `api/rag.py`.
5. WHEN the Wizard receives a chat message, THE `Local_LLM_Client` SHALL invoke the configured local LLM and return the assistant's text response to the existing routing and response-building logic unchanged.

---

### Requirement 2: Ollama Integration

**User Story:** As a developer, I want the Wizard to use Ollama as the default LLM backend, so that I can run any GGUF-compatible model locally with a simple `ollama run` command.

#### Acceptance Criteria

1. THE `Local_LLM_Client` SHALL call the Ollama `/api/generate` or `/api/chat` endpoint using an HTTP POST request.
2. THE system SHALL read `OLLAMA_BASE_URL` (default: `http://localhost:11434`) from environment variables to configure the Ollama endpoint.
3. THE system SHALL read `OLLAMA_MODEL` (default: `llama3`) from environment variables to select the model served by Ollama.
4. THE system SHALL read `OLLAMA_TIMEOUT` (default: `120` seconds) from environment variables to configure the HTTP request timeout.
5. WHEN the Ollama HTTP call succeeds, THE `Local_LLM_Client` SHALL extract and return the generated text from the response payload.
6. IF the Ollama service is unreachable or returns a non-2xx status, THEN THE `Local_LLM_Client` SHALL raise a descriptive `ConnectionError` that the API layer can catch and convert to HTTP 503.

---

### Requirement 3: llama-cpp-python Fallback Integration

**User Story:** As a developer, I want a llama-cpp-python fallback option, so that the Wizard can run even without a running Ollama daemon by loading a model file directly.

#### Acceptance Criteria

1. WHERE `LLM_BACKEND` is set to `llama_cpp`, THE `Local_LLM_Client` SHALL import and use `llama_cpp.Llama` to load the model.
2. THE system SHALL read `LLAMA_MODEL_PATH` from environment variables to locate the GGUF model file on disk.
3. THE system SHALL read `LLAMA_N_CTX` (default: `2048`) from environment variables to configure the model context window size.
4. THE system SHALL read `LLAMA_MAX_TOKENS` (default: `512`) from environment variables to cap the generated response length.
5. IF `LLAMA_MODEL_PATH` is not set or the file does not exist when `LLM_BACKEND=llama_cpp`, THEN THE `Local_LLM_Client` SHALL raise a `FileNotFoundError` with a descriptive message at startup.
6. WHEN the llama-cpp-python call succeeds, THE `Local_LLM_Client` SHALL extract and return the generated text from the completion result.

---

### Requirement 4: Preserve RAG Pipeline Integrity

**User Story:** As a Wizard user, I want the semantic search and prompt augmentation steps to remain unchanged, so that my queries are still enriched with relevant catalog context before reaching the LLM.

#### Acceptance Criteria

1. WHEN a chat message is received, THE `RAG_Pipeline` SHALL perform a ChromaDB vector search using `query_catalog` before calling the LLM.
2. THE `RAG_Pipeline` SHALL pass the retrieved `Contract` objects to `build_prompt` to construct the augmented prompt.
3. THE `build_prompt` function SHALL produce a prompt that includes the system persona, available tools list, catalog context block, and the user query.
4. WHEN no similar contracts are found in ChromaDB, THE `RAG_Pipeline` SHALL still call the LLM with a prompt that states no similar contracts were found.
5. FOR ALL valid user queries, THE `RAG_Pipeline` SHALL produce a non-empty `WizardResponse` (round-trip property: query in → structured response out).

---

### Requirement 5: Preserve Strategic Routing Logic

**User Story:** As a Wizard user, I want the tool recommendation and routing logic to continue working after the LLM swap, so that I still receive a structured `ToolSolution` recommendation.

#### Acceptance Criteria

1. WHEN the LLM returns a response, THE `Routing_Logic` SHALL apply `extract_recommendation` to map the text to a `ToolSolution` value.
2. THE `Routing_Logic` SHALL detect the `RECOMENDAÇÃO: <tool>` pattern as the primary extraction strategy.
3. THE `Routing_Logic` SHALL fall back to keyword scanning when no explicit recommendation pattern is found.
4. WHEN no tool keyword is matched, THE `Routing_Logic` SHALL return `ToolSolution.NO_SOLUTION`.
5. THE `Routing_Logic` SHALL be idempotent: applying `extract_recommendation` twice to the same LLM text SHALL return the same `ToolSolution` value.

---

### Requirement 6: Preserve Chat API Contract

**User Story:** As a frontend developer, I want the `/api/wizard/chat` endpoint to behave identically before and after the LLM swap, so that no frontend changes are required.

#### Acceptance Criteria

1. THE `/api/wizard/chat` endpoint SHALL continue to accept a `ChatMessage` body and return a `WizardResponse`.
2. WHEN a whitespace-only message is submitted, THE endpoint SHALL return HTTP 422.
3. WHEN the `Local_LLM_Client` raises a `ConnectionError` (Ollama unreachable), THE endpoint SHALL return HTTP 503 with a descriptive Portuguese error message.
4. WHEN the `Local_LLM_Client` raises a `TimeoutError` or the HTTP request exceeds the configured timeout, THE endpoint SHALL return HTTP 504.
5. IF `LLM_BACKEND=llama_cpp` and `LLAMA_MODEL_PATH` is missing, THEN THE endpoint SHALL return HTTP 503 with a descriptive error at startup rather than crashing silently.

---

### Requirement 7: Configuration via Environment Variables

**User Story:** As a platform operator, I want all local LLM settings to be configurable via environment variables, so that I can switch models or backends without code changes.

#### Acceptance Criteria

1. THE system SHALL read `LLM_BACKEND` (default: `ollama`, accepted values: `ollama`, `llama_cpp`) from environment variables to select the active LLM runtime.
2. THE system SHALL read `OLLAMA_BASE_URL` (default: `http://localhost:11434`), `OLLAMA_MODEL` (default: `llama3`), and `OLLAMA_TIMEOUT` (default: `120`) from environment variables for the Ollama backend.
3. THE system SHALL read `LLAMA_MODEL_PATH`, `LLAMA_N_CTX` (default: `2048`), and `LLAMA_MAX_TOKENS` (default: `512`) from environment variables for the llama-cpp backend.
4. IF `LLM_BACKEND` is set to an unrecognised value, THEN THE system SHALL raise a `ValueError` at startup with a message listing the accepted values.
5. THE system SHALL log the active `LLM_BACKEND` and model identifier at startup so the operator can confirm the configuration without inspecting environment variables manually.

---

### Requirement 8: Dependency Management

**User Story:** As a developer, I want the project dependencies to reflect the switch from AWS Bedrock to local LLM runtimes, so that the environment can be reproduced correctly.

#### Acceptance Criteria

1. THE `requirements.txt` SHALL remove `boto3` and `botocore` as explicit dependencies (or move them to an optional extras section).
2. THE `requirements.txt` SHALL include `httpx>=0.25.0` as an explicit dependency for the Ollama HTTP client.
3. WHERE `llama-cpp-python` support is desired, THE `requirements.txt` SHALL list `llama-cpp-python` as an optional dependency with a comment indicating it is only required when `LLM_BACKEND=llama_cpp`.
4. THE `requirements.txt` SHALL retain all non-LLM dependencies (`fastapi`, `uvicorn`, `pydantic`, `chromadb`, `sqlalchemy`, `hypothesis`, `pytest`) unchanged.
