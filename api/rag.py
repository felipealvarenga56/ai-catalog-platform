"""Pipeline RAG: integração ChromaDB + Local LLM para o Wizard Aura."""

import chromadb
import logging
import os
from api.database import get_connection
from api.llm_client import get_llm_client
from api.models import Contract

logger = logging.getLogger(__name__)

# ChromaDB setup — persistent local store
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "local_db", "chroma")
COLLECTION_NAME = "nexus_contracts"

# Module-level LLM client singleton — initialised once at import time.
# Tests should patch `api.rag._llm_client` directly.
_llm_client = get_llm_client()


def _get_chroma_client() -> chromadb.ClientAPI:
    """Return a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_DIR)


def _get_collection(client: chromadb.ClientAPI | None = None) -> chromadb.Collection:
    """Get or create the contracts collection."""
    if client is None:
        client = _get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_contract(
    contract_id: int,
    title: str,
    description: str,
    area: str,
    initiative: str,
    owner: str,
    status: str,
    business_map_id: str,
    usage: str | None = None,
) -> None:
    """Index a single contract into ChromaDB for semantic search."""
    collection = _get_collection()
    doc_text = f"{title}. {description}"
    if area:
        doc_text += f" Área: {area}"
    if usage:
        doc_text += f" {usage}"

    doc_id = str(contract_id)
    collection.upsert(
        ids=[doc_id],
        documents=[doc_text],
        metadatas=[{
            "initiative": initiative,
            "area": area,
            "status": status,
            "business_map_id": business_map_id,
            "title": title,
        }],
    )


def index_all_contracts() -> int:
    """Index all contracts from SQLite into ChromaDB. Returns count indexed."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM contracts").fetchall()
        collection = _get_collection()
        if not rows:
            return 0

        ids = [str(row["id"]) for row in rows]
        documents = []
        metadatas = []
        for row in rows:
            doc = f"{row['title']}. {row['description']}"
            if row["area"]:
                doc += f" Área: {row['area']}"
            if row["usage"]:
                doc += f" {row['usage']}"
            documents.append(doc)
            metadatas.append({
                "initiative": row["initiative"],
                "area": row["area"],
                "status": row["status"],
                "business_map_id": row["business_map_id"],
                "title": row["title"],
            })

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return len(rows)
    finally:
        conn.close()


def query_catalog(text: str, n_results: int = 5) -> list[Contract]:
    """Semantic search in ChromaDB, returning matching Contracts from SQLite."""
    collection = _get_collection()
    try:
        results = collection.query(query_texts=[text], n_results=n_results)
    except Exception:
        return []

    if not results or not results["ids"] or not results["ids"][0]:
        return []

    contract_ids = []
    for meta in results["metadatas"][0]:
        contract_ids.append(meta.get("business_map_id"))

    if not contract_ids:
        return []

    conn = get_connection()
    try:
        placeholders = ",".join("?" for _ in contract_ids)
        rows = conn.execute(
            f"SELECT * FROM contracts WHERE business_map_id IN ({placeholders})",
            contract_ids,
        ).fetchall()
        return [
            Contract(
                id=r["id"],
                business_map_id=r["business_map_id"],
                title=r["title"],
                area=r["area"],
                initiative=r["initiative"],
                version=r["version"],
                description=r["description"],
                owner=r["owner"],
                status=r["status"],
                contact_name=r["contact_name"],
                contact_email=r["contact_email"],
                sec_approval=r["sec_approval"],
                docs_link=r["docs_link"],
                usage=r["usage"],
                limitations=r["limitations"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]
    finally:
        conn.close()


def build_prompt(query: str, context: list[Contract]) -> str:
    """Build an augmented prompt with catalog context for the LLM."""
    context_block = ""
    if context:
        items = []
        for c in context:
            items.append(
                f"- **{c.title}** (iniciativa: {c.initiative}, status: {c.status}): {c.description}"
            )
        context_block = (
            "Contratos relevantes encontrados no Catálogo:\n"
            + "\n".join(items)
            + "\n\n"
        )
    else:
        context_block = "Nenhum contrato similar foi encontrado no Catálogo.\n\n"

    return (
        "Você é o Wizard Aura, um assistente de governança de IA e dados. "
        "Sua função é analisar propostas de projetos, responder perguntas sobre o catálogo "
        "e recomendar a ferramenta ou equipe mais adequada.\n\n"
        "Ferramentas disponíveis: Copilot, Lovable, n8n, Alteryx, Equipe Deep, Equipe BI, "
        "Squad de Desenvolvimento. Se nenhuma se aplica, diga 'Não temos uma solução disponível hoje'.\n\n"
        "Ao recomendar uma ferramenta, inclua uma justificativa clara. "
        "Use o formato: RECOMENDAÇÃO: <nome_ferramenta> seguido da justificativa.\n\n"
        f"{context_block}"
        f"Pergunta do usuário: {query}\n\n"
        "Responda em português de forma clara e objetiva."
    )
