1. Architectural Philosophy: "Local-First & Transparent"

The architecture must prioritize simplicity over scale. Since the developer is a Junior Data Scientist, avoid complex microservices or container orchestration (Docker/K8s). Focus on a monolithic Python backend that a Data Scientist can easily debug using standard print statements or a debugger.

2. Mandatory Tech Stack (Local Execution)

Backend: Python 3.10+ using FastAPI. It is lightweight, provides automatic Swagger docs, and is easy for DS profiles to understand.

Frontend: Local Vanilla HTML5/JavaScript and Tailwind CSS (via CDN). No complex frameworks like React or Vue to minimize the "build step" overhead.

Database: SQLite. It’s a single file, requires zero installation, and is natively supported by Python's sqlite3 or SQLAlchemy.

Intelligence (The Wizard): Ollama or Llama-cpp-python. The LLM must run locally to ensure data privacy and zero API costs.

Search/Retrieval: ChromaDB (Local Vector Store) for the "Catalog" RAG (Retrieval-Augmented Generation).

3. Component Breakdown (The Funnel Mapping)
The architecture should be divided into three logical modules matching the product funnel:

Module A: The Ingestion Engine (Catalog)
Define a service that reads local files (CSV, JSON, or Excel) from the "Deep," "BI," and "n8n" sources.The architecture must show a Data Sync Layer that converts these files into a SQLite database and a Vector Store.

Module B: The RAG Orchestrator (Wizard)
Specify a Retrieval Pipeline: User Input $\rightarrow$ Vector Search (Catalog) $\rightarrow$ Prompt Augmentation $\rightarrow$ Local LLM $\rightarrow$ Structured Response.This module must include a "Routing Logic" component that maps LLM outputs to the specific tools (n8n, Lovable, etc.).

Module C: The Static Asset Server (Delivery)
The backend must serve a directory of local PDFs and templates.Define an API endpoint /delivery/instructions/{tool_id} that returns the specific markdown/PDF path for the user.

4. Guidelines for the Junior Data Scientist Persona
File Structure: Suggest a flat or shallow directory structure (e.g., /api, /data, /frontend).

Documentation Style: The Architecture.md should use Mermaid.js diagrams for flowcharts.Code 

Patterns: Recommend using Pydantic schemas for data validation—a skill every DS should master.

No "Black Boxes": Explicitly define where the data resides on the local disk (e.g., ./local_db/nexus.db).
