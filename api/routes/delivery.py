"""Endpoints do Módulo Entrega - Procedimentos de acesso."""

import json
from fastapi import APIRouter, HTTPException
from api.database import get_connection
from api.models import DeliveryProcedure

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


def _row_to_procedure(row) -> DeliveryProcedure:
    """Convert a sqlite3.Row to a DeliveryProcedure model."""
    return DeliveryProcedure(
        tool_id=row["tool_id"],
        tool_name=row["tool_name"],
        steps=json.loads(row["steps"]),
        documentation_path=row["documentation_path"],
        contact_info=row["contact_info"],
    )


@router.get("/tools", response_model=list[DeliveryProcedure])
def list_tools():
    """List all tools that have delivery procedures registered."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM delivery_procedures ORDER BY tool_name").fetchall()
        return [_row_to_procedure(row) for row in rows]
    finally:
        conn.close()


@router.get("/instructions/{tool_id}", response_model=DeliveryProcedure)
def get_instructions(tool_id: str):
    """Return the delivery procedure for a given tool_id.

    If no procedure is registered, returns a fallback response indicating
    the procedure is under development.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM delivery_procedures WHERE tool_id = ?",
            (tool_id.lower(),),
        ).fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Procedimento em elaboração. "
                    "Entre em contato com a equipe responsável."
                ),
            )

        return _row_to_procedure(row)
    finally:
        conn.close()
