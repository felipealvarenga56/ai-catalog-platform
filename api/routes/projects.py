"""Endpoints do Catálogo de Projetos."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from api.database import get_connection
from api.models import Contract

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _row_to_contract(row) -> Contract:
    """Convert a sqlite3.Row to a Contract model."""
    return Contract(
        id=row["id"],
        business_map_id=row["business_map_id"],
        title=row["title"],
        area=row["area"],
        initiative=row["initiative"],
        version=row["version"],
        description=row["description"],
        owner=row["owner"],
        status=row["status"],
        contact_name=row["contact_name"],
        contact_email=row["contact_email"],
        sec_approval=row["sec_approval"],
        docs_link=row["docs_link"],
        cost=row["cost"],
        projected_return=row["projected_return"],
        usage=row["usage"],
        limitations=row["limitations"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.get("", response_model=list[Contract])
def list_projects(
    search: Optional[str] = Query(None, description="Busca por título, descrição ou área"),
    initiative: Optional[str] = Query(None, description="Filtro por initiative"),
):
    """List all contracts with optional search and initiative filter."""
    conn = get_connection()
    try:
        query = "SELECT * FROM contracts WHERE 1=1"
        params: list = []

        if search:
            query += " AND (title LIKE ? OR description LIKE ? OR area LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        if initiative:
            query += " AND initiative = ?"
            params.append(initiative)

        query += " ORDER BY id"
        rows = conn.execute(query, params).fetchall()
        return [_row_to_contract(row) for row in rows]
    finally:
        conn.close()


@router.get("/{project_id}", response_model=Contract)
def get_project(project_id: int):
    """Get details of a single contract by ID."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM contracts WHERE id = ?", (project_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Contrato não encontrado.")
        return _row_to_contract(row)
    finally:
        conn.close()
