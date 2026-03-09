# Aura Governance Platform

Aura is an intelligent AI & Data Governance platform that bridges the gap between corporate strategy and technical execution. It centralizes project intelligence, evaluates technical feasibility through an AI-powered Wizard, and automates the path to project delivery.

This repository is an experimental proof of concept designed to run entirely locally — no cloud dependencies, no API costs, no complex infrastructure. It's built for a Junior Data Scientist to understand, debug, and extend.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (HTML/JS)                │
│              Vanilla JS + Tailwind CDN              │
├─────────────────────────────────────────────────────┤
│                  FastAPI Backend                    │
│  /api/projects  /api/wizard  /api/delivery  /api/reports │
├──────────┬──────────┬───────────┬───────────────────┤
│  SQLite  │ ChromaDB │  Ollama   │  Static Files     │
│ (catalog)│ (vectors)│ (local LLM)│ (PDFs/templates) │
└──────────┴──────────┴───────────┴───────────────────┘
```

The platform follows a three-phase funnel architecture:

1. **Catálogo** — Ingest and unify project data from multiple sources
2. **Wizard** — AI-powered analysis and routing of project proposals
3. **Entrega** — Operational procedures to get users started with recommended tools

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Backend | Python 3.10+ / FastAPI | Lightweight, auto-generates Swagger docs, easy to debug |
| Frontend | Vanilla HTML/JS + Tailwind CSS (CDN) | Zero build step, no framework overhead |
| Database | SQLite | Single file, zero installation, native Python support |
| LLM | Ollama (local) | Data privacy, zero API costs, runs on consumer hardware |
| Vector Store | ChromaDB | Local persistent vector search for RAG |
| Data Validation | Pydantic | Type-safe schemas, essential for any data project |

## Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Pull an LLM model (gemma3:4b recommended for 16GB RAM machines)
ollama pull gemma3:4b

# Start Ollama (if not already running)
ollama serve

# Start the application
uvicorn api.main:app --reload
```

Open `http://localhost:8000` in your browser.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_BACKEND` | `ollama` | LLM backend: `ollama` or `llama_cpp` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma3:4b` | Model to use for generation |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |
| `LLAMA_MODEL_PATH` | — | Path to GGUF file (only for `llama_cpp` backend) |

