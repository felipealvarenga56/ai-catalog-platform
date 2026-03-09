"""
Local LLM Client abstraction for the Aura Wizard.

Supports two backends:
- Ollama (default): HTTP API at localhost:11434
- llama-cpp-python (fallback): in-process GGUF model loading

Select backend via the LLM_BACKEND environment variable.
"""

import logging
import os
from abc import ABC, abstractmethod

import httpx


class BaseLLMClient(ABC):
    """Abstract base class for local LLM clients.

    Concrete implementations must override `generate` to invoke
    the underlying LLM runtime and return the generated text.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the generated text.

        Args:
            prompt: The full augmented prompt string to send to the model.

        Returns:
            The generated text response as a plain string.

        Raises:
            ConnectionError: If the backend is unreachable or returns an error.
            TimeoutError: If the request exceeds the configured timeout.
            FileNotFoundError: If the model file is missing (llama_cpp backend).
        """


class OllamaClient(BaseLLMClient):
    """LLM client that calls a locally running Ollama daemon via HTTP.

    Configuration is read from environment variables at construction time:
    - OLLAMA_BASE_URL  (default: http://localhost:11434)
    - OLLAMA_MODEL     (default: llama3)
    - OLLAMA_TIMEOUT   (default: 120 seconds)
    """

    def __init__(self) -> None:
        self.base_url: str = os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ).rstrip("/")
        self.model: str = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
        self.timeout: int = int(os.environ.get("OLLAMA_TIMEOUT", "120"))

    def generate(self, prompt: str) -> str:
        """Send *prompt* to Ollama's /api/generate endpoint and return the text.

        Args:
            prompt: The full augmented prompt string.

        Returns:
            The generated text extracted from the ``"response"`` field of the
            Ollama JSON payload.

        Raises:
            ConnectionError: If Ollama is unreachable or returns a non-2xx status.
            TimeoutError: If the HTTP request exceeds ``self.timeout`` seconds.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = httpx.post(url, json=payload, timeout=self.timeout)
        except httpx.TimeoutException as exc:
            raise TimeoutError(
                f"Ollama request timed out after {self.timeout}s: {exc}"
            ) from exc
        except httpx.RequestError as exc:
            raise ConnectionError(
                f"Failed to reach Ollama at {self.base_url}: {exc}"
            ) from exc

        if response.status_code < 200 or response.status_code >= 300:
            raise ConnectionError(
                f"Ollama returned HTTP {response.status_code}: {response.text}"
            )

        return response.json()["response"]


class LlamaCppClient(BaseLLMClient):
    """LLM client that loads a GGUF model file in-process via llama-cpp-python.

    Configuration is read from environment variables at construction time:
    - LLAMA_MODEL_PATH  (required) — absolute path to the GGUF model file
    - LLAMA_N_CTX       (default: 2048) — context window size
    - LLAMA_MAX_TOKENS  (default: 512)  — maximum tokens to generate

    Raises:
        FileNotFoundError: If LLAMA_MODEL_PATH is not set or the file does not exist.
    """

    def __init__(self) -> None:
        model_path: str | None = os.environ.get("LLAMA_MODEL_PATH")
        if not model_path:
            raise FileNotFoundError(
                "LLAMA_MODEL_PATH environment variable is not set. "
                "Set it to the absolute path of your GGUF model file "
                "(e.g. /models/llama-3-8b.gguf) before starting the server."
            )
        if not os.path.isfile(model_path):
            raise FileNotFoundError(
                f"LLAMA_MODEL_PATH points to a file that does not exist: '{model_path}'. "
                "Ensure the GGUF model file is present at that path."
            )

        self.model_path: str = model_path
        self.n_ctx: int = int(os.environ.get("LLAMA_N_CTX", "2048"))
        self.max_tokens: int = int(os.environ.get("LLAMA_MAX_TOKENS", "512"))

        # Lazy import so the module can be imported even when
        # llama-cpp-python is not installed (e.g. when LLM_BACKEND=ollama).
        from llama_cpp import Llama  # noqa: PLC0415

        self._llm = Llama(model_path=self.model_path, n_ctx=self.n_ctx)

    def generate(self, prompt: str) -> str:
        """Invoke the loaded Llama model and return the generated text.

        Args:
            prompt: The full augmented prompt string.

        Returns:
            The generated text extracted from the first completion choice.
        """
        result = self._llm(prompt=prompt, max_tokens=self.max_tokens)
        return result["choices"][0]["text"]


_logger = logging.getLogger(__name__)


def get_llm_client() -> BaseLLMClient:
    """Factory that reads ``LLM_BACKEND`` and returns the appropriate client.

    Accepted values for ``LLM_BACKEND``:
    - ``ollama``    (default) — uses :class:`OllamaClient`
    - ``llama_cpp`` — uses :class:`LlamaCppClient`

    Returns:
        A concrete :class:`BaseLLMClient` instance for the configured backend.

    Raises:
        ValueError: If ``LLM_BACKEND`` is set to an unrecognised value.
        FileNotFoundError: If ``LLM_BACKEND=llama_cpp`` and ``LLAMA_MODEL_PATH``
            is missing or the file does not exist.
    """
    backend: str = os.environ.get("LLM_BACKEND", "ollama")

    if backend == "ollama":
        client = OllamaClient()
        _logger.info(
            "LLM backend: ollama | model: %s | url: %s",
            client.model,
            client.base_url,
        )
        return client

    if backend == "llama_cpp":
        client = LlamaCppClient()
        _logger.info(
            "LLM backend: llama_cpp | model path: %s",
            client.model_path,
        )
        return client

    raise ValueError(
        f"Unrecognised LLM_BACKEND='{backend}'. Accepted values: ollama, llama_cpp"
    )


# Module-level singleton — initialised once at import time.
_llm_client: BaseLLMClient = get_llm_client()
