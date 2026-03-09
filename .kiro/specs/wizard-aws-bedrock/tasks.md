# Implementation Plan: Wizard AWS Bedrock

## Overview

Surgical swap of the Ollama HTTP client for an AWS Bedrock boto3 client in `api/rag.py` and `api/routes/wizard.py`. All RAG, routing, and frontend logic is preserved unchanged.

## Tasks

- [x] 1. Update dependencies
  - Add `boto3>=1.34.0` to `requirements.txt`
  - Verify `httpx` is still listed (used by other parts of the app) but note it is no longer used for LLM calls
  - _Requirements: 6.1, 6.3_

- [x] 2. Rewrite the LLM backend in `api/rag.py`
  - [x] 2.1 Replace Ollama config constants and imports with Bedrock equivalents
    - Remove `import httpx` and the three `OLLAMA_*` constants
    - Add `import boto3`, `import botocore.exceptions`, `import logging`
    - Add constants: `AWS_REGION`, `BEDROCK_MODEL_ARN` (default `cloude-sonnet-45`), `BEDROCK_TIMEOUT` (default `60`) read from `os.environ`
    - Add startup warning log if `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` is absent from env
    - _Requirements: 1.5, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 2.2 Implement `_get_bedrock_client()` helper
    - Create a `boto3.client("bedrock-runtime", region_name=AWS_REGION)` and return it
    - _Requirements: 1.1_

  - [x] 2.3 Implement new `get_llm_response(prompt: str) -> str` using Bedrock `converse` API
    - Call `client.converse(modelId=BEDROCK_MODEL_ARN, messages=[{"role": "user", "content": [{"text": prompt}]}], inferenceConfig={"maxTokens": 1024, "temperature": 0.3})`
    - Extract and return `response["output"]["message"]["content"][0]["text"]`
    - Let `botocore` exceptions propagate to the caller (caught in `wizard.py`)
    - _Requirements: 1.2, 1.3, 1.4_

  - [ ]* 2.4 Write property test: env var override is respected (Property 4)
    - **Property 4: Environment variable override is respected**
    - **Validates: Requirements 5.3**
    - Use `hypothesis` + `unittest.mock.patch` on `boto3.client`; generate random ARN strings; assert the `modelId` passed to `converse` equals the env var value

- [x] 3. Update error handling in `api/routes/wizard.py`
  - Remove `import httpx`; add `import botocore.exceptions`
  - Replace `httpx.ConnectError` and `httpx.HTTPStatusError` handlers with `botocore.exceptions.ClientError` and `botocore.exceptions.EndpointResolutionError` → HTTP 503
  - Replace `httpx.TimeoutException` handler with `botocore.exceptions.ReadTimeoutError` → HTTP 504
  - Keep all other logic (whitespace guard, `query_catalog`, `build_prompt`, `extract_recommendation`, response building) unchanged
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4. Checkpoint — ensure the app starts and existing tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Write unit tests (`tests/test_wizard_bedrock.py`)
  - [x] 5.1 Test happy path: mock `boto3.client` returning a canned response; assert `get_llm_response` returns the extracted text string
    - _Requirements: 1.3_

  - [ ]* 5.2 Write property test: RAG pipeline output is structurally valid (Property 1)
    - **Property 1: RAG pipeline output is structurally valid**
    - **Validates: Requirements 4.1, 2.1**
    - Generate random non-empty message strings with `hypothesis`; mock Bedrock and ChromaDB; assert response is a valid `WizardResponse` (non-empty `answer`, valid `recommended_tool`, list `similar_projects`)

  - [ ]* 5.3 Write property test: whitespace-only messages are always rejected (Property 2)
    - **Property 2: Whitespace-only messages are always rejected**
    - **Validates: Requirements 4.2**
    - Generate strings from `st.text(alphabet=" \t\n\r", min_size=1)`; assert endpoint returns HTTP 422

  - [ ]* 5.4 Write property test: Bedrock client error maps to 503 (Property 3)
    - **Property 3: Bedrock client error maps to 503**
    - **Validates: Requirements 4.3, 4.4**
    - Generate random `ClientError` error codes with `hypothesis`; mock boto3 to raise them; assert endpoint returns 503 with a non-empty Portuguese message

  - [x] 5.5 Test timeout: mock `ReadTimeoutError`; assert endpoint returns HTTP 504
    - _Requirements: 4.5_

  - [x] 5.6 Test missing credential warning: unset `AWS_ACCESS_KEY_ID` in env; assert a `WARNING` log entry is emitted at module import
    - _Requirements: 5.5_

- [x] 6. Write property tests for routing and prompt logic (`tests/test_wizard_bedrock_properties.py`)
  - [x]* 6.1 Write property test: routing logic is deterministic given LLM output (Property 5)
    - **Property 5: Routing logic is deterministic given LLM output**
    - **Validates: Requirements 3.1, 3.2**
    - Generate random `ToolSolution` values; build a response string `"RECOMENDAÇÃO: <tool_keyword>"`; assert `extract_recommendation` returns the correct `ToolSolution`

  - [x]* 6.2 Write property test: prompt always contains catalog context block (Property 6)
    - **Property 6: Prompt always contains catalog context block**
    - **Validates: Requirements 2.2, 2.3, 2.4**
    - Generate random lists of `Contract` objects (including empty list) with `hypothesis`; assert `build_prompt` output always contains either the catalog header string or the "no contracts" fallback string

- [x] 7. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Property tests require `hypothesis` — add it to `requirements.txt` if not already present
- All boto3 calls in tests must be mocked; no real AWS calls should be made during testing
- The `converse` API is preferred over `invoke_model` as it handles the messages format natively and works with cross-region inference profile ARNs
