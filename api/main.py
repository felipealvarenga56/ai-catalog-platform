"""FastAPI application entry point for Aura Governance Platform."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.database import create_tables
from api.ingestion import seed_sample_data
from api.routes import projects, reports, wizard, delivery

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: create tables and seed sample data
    create_tables()
    seed_sample_data()

    # Validate LLM client is accessible; warn (don't crash) on misconfiguration
    try:
        from api.rag import _llm_client  # noqa: F401 — import triggers singleton init
        _logger.info("LLM client initialised successfully.")
    except FileNotFoundError as exc:
        _logger.critical(
            "LLM client failed to initialise: %s — "
            "The /api/wizard/chat endpoint will return HTTP 503 until this is resolved.",
            exc,
        )
    except ValueError as exc:
        _logger.critical(
            "Invalid LLM_BACKEND configuration: %s — "
            "Set LLM_BACKEND to 'ollama' or 'llama_cpp'.",
            exc,
        )

    yield


app = FastAPI(
    title="Aura Governance Platform",
    description="Plataforma de Governança de IA e Dados",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all origins for local PoC
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(projects.router)
app.include_router(reports.router)
app.include_router(wizard.router)
app.include_router(delivery.router)

# Serve frontend static files if directory exists
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
