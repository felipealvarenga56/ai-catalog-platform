# Implementation Plan: Wizard Local LLM Migration

## Overview

Replace the AWS Bedrock invocation layer with a `Local_LLM_Client` abstraction (`api/llm_client.py`) supporting Ollama (primary) and llama-cpp-python (fallback). Minimal changes to `api/rag.py`; all other components unchanged. Remove Bedrock test files and replace with local-LLM property and unit tests.

## Tasks

- [x] 1. Update dependencies in requirements.txt
  - Remove `boto3` and `botocore` lines
  - Add `httpx>=0.25.0`
  - Add `llama-cpp-python` as an optional dependency with a comment: `# optional: only required when LLM_BACKEND=llama_cpp`
  - Verify all other deps (`fastapi`, `uvicorn`, `pydantic`, `chromadb`, `sqlalchemy`, `hypothesis`, `pytest`) are retained
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 2. Create api/llm_client.py with BaseLLMClient, OllamaClient, LlamaCppClient, and factory
  - [x] 2.1 Implement `BaseLLMClient` abstract base class with `generate(self, prompt: str) -> str`
    - _Requirements: 1.1, 1.5_

  - [x] 2.2 Implement `OllamaClient(BaseLLMClient)`
    - `__init__` reads `OLLAMA_BASE_URL` (default `http://localhost:11434`), `OLLAMA_MODEL` (default `llama3`), `OLLAMA_TIMEOUT` (default `120`) from env
    - `generate` POSTs to `{base_url}/api/generate` using `httpx`
    - Extracts and returns the generated text string from the response payload
    - Raises `ConnectionError` on non-2xx status or network failure
    - Raises `TimeoutError` on request timeout
    - _Requirements: 1.2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ]* 2.3 Write property test P1: Ollama client routes to configured URL
    - **Property 1: Ollama client routes to the configured URL**
    - **Validates: Requirements 1.2, 2.1**
    - Use `st.text()` for prompt; mock `httpx.post`; assert called URL matches `OLLAMA_BASE_URL`
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 1: Ollama routes to configured URL`
    - File: `tests/test_llm_client.py`

  - [ ]* 2.4 Write property test P4: Ollama errors surface as ConnectionError
    - **Property 4: Ollama connection errors surface as ConnectionError**
    - **Validates: Requirements 2.6**
    - Use `st.integers(400, 599)` for status codes; assert `ConnectionError` is raised
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 4: Ollama errors → ConnectionError`
    - File: `tests/test_llm_client.py`

  - [x] 2.5 Implement `LlamaCppClient(BaseLLMClient)`
    - `__init__` reads `LLAMA_MODEL_PATH` (required), `LLAMA_N_CTX` (default `2048`), `LLAMA_MAX_TOKENS` (default `512`) from env
    - Raises `FileNotFoundError` with descriptive message if path is missing or file does not exist
    - `generate` calls `self._llm(prompt=prompt, max_tokens=self.max_tokens)` and extracts the text
    - _Requirements: 1.3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 2.6 Write property test P2: llama-cpp client invokes the loaded model
    - **Property 2: llama-cpp client invokes the loaded model**
    - **Validates: Requirements 1.3**
    - Use `st.text()` for prompt; mock `llama_cpp.Llama`; assert called with the prompt
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 2: llama-cpp invokes loaded model`
    - File: `tests/test_llm_client.py`

  - [ ]* 2.7 Write property test P3: Client extracts generated text
    - **Property 3: Client extracts and returns generated text**
    - **Validates: Requirements 2.5, 3.6**
    - Use `st.fixed_dictionaries(...)` for Ollama/llama-cpp response payloads; assert returned value is a non-empty string
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 3: client extracts generated text`
    - File: `tests/test_llm_client.py`

  - [x] 2.8 Implement `get_llm_client()` factory function
    - Reads `LLM_BACKEND` env var (default `ollama`)
    - Returns `OllamaClient` or `LlamaCppClient` accordingly
    - Raises `ValueError` with accepted values listed for any other value
    - Logs active backend and model identifier at startup
    - Cached as module-level singleton
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 2.9 Write property test P10: Unrecognised LLM_BACKEND raises ValueError
    - **Property 10: Unrecognised LLM_BACKEND raises ValueError at startup**
    - **Validates: Requirements 7.4**
    - Use `st.text().filter(lambda s: s not in ('ollama', 'llama_cpp'))` for backend value
    - Assert `ValueError` is raised and message lists accepted values
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 10: bad LLM_BACKEND → ValueError`
    - File: `tests/test_llm_client.py`

  - [ ]* 2.10 Write unit tests for llm_client configuration and error mapping
    - Test each env var override (e.g., `OLLAMA_MODEL` overrides default `llama3`)
    - Test `ConnectionError` raised on non-2xx Ollama response
    - Test `TimeoutError` raised on Ollama timeout
    - Test `FileNotFoundError` raised when `LLAMA_MODEL_PATH` is missing
    - Assert `boto3` is not imported in `api.rag` (no `boto3` attribute)
    - File: `tests/test_llm_client.py`
    - _Requirements: 1.4, 2.6, 3.5, 7.4_

- [x] 3. Checkpoint — Ensure all llm_client tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Modify api/rag.py to use Local_LLM_Client
  - Remove `import boto3`, `import botocore.exceptions`, all `AWS_*`/`BEDROCK_*` config constants, `_get_bedrock_client()`, and `get_llm_response()`
  - Add `from api.llm_client import get_llm_client` and `_llm_client = get_llm_client()` at module level
  - Replace the `get_llm_response(prompt)` call site with `_llm_client.generate(prompt)`
  - All other functions (`index_contract`, `index_all_contracts`, `query_catalog`, `build_prompt`) remain unchanged
  - _Requirements: 1.1, 1.4, 1.5, 4.1, 4.2, 4.3, 4.4_

  - [ ]* 4.1 Write property test P5: build_prompt always includes all four required sections
    - **Property 5: build_prompt always includes all four required sections**
    - **Validates: Requirements 4.3, 4.4**
    - Use `st.text()` for query, `st.lists(st.builds(Contract, ...))` for contracts (including empty list)
    - Assert returned string contains: system persona text, tools list, catalog context block, user query
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 5: build_prompt contains all sections`
    - File: `tests/test_rag.py`

  - [ ]* 4.2 Write property test P6: RAG pipeline round-trip
    - **Property 6: RAG pipeline round-trip — query in, WizardResponse out**
    - **Validates: Requirements 4.5, 6.1**
    - Use `st.text(min_size=1)` for query; mock `_llm_client.generate` to return a fixed string
    - Assert returned `WizardResponse` has non-empty `response`, `tool_recommendation`, `justification`
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 6: RAG pipeline round-trip`
    - File: `tests/test_rag.py`

  - [ ]* 4.3 Write unit tests for rag.py
    - Test that `query_catalog` is called before LLM invocation
    - Test that `build_prompt` receives the retrieved contracts
    - Test that ChromaDB failure degrades gracefully (empty context, LLM still called)
    - File: `tests/test_rag.py`
    - _Requirements: 4.1, 4.2, 4.4_

- [x] 5. Add explicit ConnectionError/TimeoutError handling in api/main.py
  - In the `/api/wizard/chat` endpoint, add explicit `except ConnectionError` → HTTP 503 with Portuguese message (e.g., `"Serviço LLM local indisponível. Verifique se o Ollama está em execução."`)
  - Add explicit `except TimeoutError` → HTTP 504
  - Handle `FileNotFoundError` (missing `LLAMA_MODEL_PATH`) → HTTP 503 at startup
  - `ChatMessage` and `WizardResponse` schemas remain unchanged
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 5.1 Write property test P9: Whitespace-only messages rejected with HTTP 422
    - **Property 9: Whitespace-only messages are rejected with HTTP 422**
    - **Validates: Requirements 6.2**
    - Use `st.text(alphabet=st.characters(whitelist_categories=('Zs',)), min_size=1)` for message
    - Assert `POST /api/wizard/chat` returns HTTP 422
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 9: whitespace → HTTP 422`
    - File: `tests/test_api.py`

  - [ ]* 5.2 Write unit tests for HTTP error mapping
    - Test `ConnectionError` from LLM client → HTTP 503 with Portuguese message
    - Test `TimeoutError` from LLM client → HTTP 504
    - Test missing `LLAMA_MODEL_PATH` at startup → HTTP 503
    - File: `tests/test_api.py`
    - _Requirements: 6.3, 6.4, 6.5_

- [ ] 6. Extend routing tests
  - [ ]* 6.1 Write property test P7: extract_recommendation always returns a valid ToolSolution
    - **Property 7: extract_recommendation always returns a valid ToolSolution**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    - Use `st.text()` for LLM response string
    - Assert `extract_recommendation(text).tool` is a member of `ToolSolution` enum
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 7: extract_recommendation → valid ToolSolution`
    - File: `tests/test_routing.py`

  - [ ]* 6.2 Write property test P8: extract_recommendation is idempotent
    - **Property 8: extract_recommendation is idempotent**
    - **Validates: Requirements 5.5**
    - Use `st.text()` for LLM response string
    - Assert calling `extract_recommendation(text)` twice returns the same `ToolSolution`
    - `@settings(max_examples=100)`
    - Tag: `# Feature: wizard-local-llm-migration, Property 8: extract_recommendation idempotent`
    - File: `tests/test_routing.py`

- [ ] 7. Remove obsolete Bedrock test files
  - Delete `tests/test_wizard_bedrock.py`
  - Delete `tests/test_wizard_bedrock_properties.py`
  - _Requirements: 1.1, 1.4, 8.1_

- [ ] 8. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use `@settings(max_examples=100)` and are tagged with the feature and property number
- The LLM client singleton (`_llm_client`) is initialised at module import time in `api/rag.py`; tests that need a different backend should patch `api.rag._llm_client`
