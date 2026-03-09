"""Endpoint de Relatório Executivo."""

from typing import Optional

from fastapi import APIRouter, Query
from api.database import get_connection
from api.models import (
    ExecutiveReport,
    ExecutiveDashboardReport,
    ComplianceMetrics,
    FinancialMetrics,
    CrossTabEntry,
    FilterOptions,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def build_where_clause(
    area: str | None,
    initiative: str | None,
    status: str | None,
    owner: str | None,
) -> tuple[str, list]:
    """Return (where_sql, params) for optional filters."""
    conditions = []
    params = []
    if area:
        conditions.append("area = ?")
        params.append(area)
    if initiative:
        conditions.append("initiative = ?")
        params.append(initiative)
    if status:
        conditions.append("status = ?")
        params.append(status)
    if owner:
        conditions.append("owner = ?")
        params.append(owner)
    where_sql = " AND ".join(conditions)
    if where_sql:
        where_sql = "WHERE " + where_sql
    return where_sql, params


@router.get("/executive", response_model=ExecutiveReport)
def executive_report():
    """Generate an executive report with counts by initiative, by status, and total."""
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) as cnt FROM contracts").fetchone()["cnt"]

        by_initiative: dict[str, int] = {}
        for row in conn.execute("SELECT initiative, COUNT(*) as cnt FROM contracts GROUP BY initiative"):
            by_initiative[row["initiative"]] = row["cnt"]

        by_status: dict[str, int] = {}
        for row in conn.execute("SELECT status, COUNT(*) as cnt FROM contracts GROUP BY status"):
            by_status[row["status"]] = row["cnt"]

        summary = (
            f"Portfólio com {total} contratos registrados, "
            f"distribuídos em {len(by_initiative)} iniciativas e {len(by_status)} status diferentes."
        )

        return ExecutiveReport(
            total_projects=total,
            by_source=by_initiative,
            by_status=by_status,
            summary=summary,
        )
    finally:
        conn.close()

@router.get("/executive-dashboard", response_model=ExecutiveDashboardReport)
def executive_dashboard(
    area: Optional[str] = Query(None),
    initiative: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
):
    """Generate an enriched executive dashboard report with KPIs, charts, and cross-tabs."""
    where_sql, params = build_where_clause(area, initiative, status, owner)
    conn = get_connection()
    try:
        # --- Total ---
        total = conn.execute(
            f"SELECT COUNT(*) as cnt FROM contracts {where_sql}", params
        ).fetchone()["cnt"]

        # --- By status ---
        by_status: dict[str, int] = {}
        for row in conn.execute(
            f"SELECT status, COUNT(*) as cnt FROM contracts {where_sql} GROUP BY status",
            params,
        ):
            by_status[row["status"]] = row["cnt"]

        # --- By initiative ---
        by_initiative: dict[str, int] = {}
        for row in conn.execute(
            f"SELECT initiative, COUNT(*) as cnt FROM contracts {where_sql} GROUP BY initiative",
            params,
        ):
            by_initiative[row["initiative"]] = row["cnt"]

        # --- By area ---
        by_area: dict[str, int] = {}
        for row in conn.execute(
            f"SELECT area, COUNT(*) as cnt FROM contracts {where_sql} GROUP BY area",
            params,
        ):
            by_area[row["area"]] = row["cnt"]

        # --- By owner ---
        by_owner: dict[str, int] = {}
        for row in conn.execute(
            f"SELECT owner, COUNT(*) as cnt FROM contracts {where_sql} GROUP BY owner",
            params,
        ):
            by_owner[row["owner"]] = row["cnt"]

        # --- Compliance metrics ---
        if where_sql:
            sec_where = f"{where_sql} AND sec_approval IS NOT NULL"
            docs_where = f"{where_sql} AND docs_link IS NOT NULL"
        else:
            sec_where = "WHERE sec_approval IS NOT NULL"
            docs_where = "WHERE docs_link IS NOT NULL"

        sec_count = conn.execute(
            f"SELECT COUNT(*) as cnt FROM contracts {sec_where}", params
        ).fetchone()["cnt"]

        docs_count = conn.execute(
            f"SELECT COUNT(*) as cnt FROM contracts {docs_where}", params
        ).fetchone()["cnt"]

        compliance = ComplianceMetrics(
            sec_approval_count=sec_count,
            sec_approval_percentage=round(sec_count / total * 100, 2) if total > 0 else 0.0,
            docs_link_count=docs_count,
            docs_link_percentage=round(docs_count / total * 100, 2) if total > 0 else 0.0,
        )

        # --- Financial metrics ---
        # Build extra-condition clauses that extend where_sql safely
        if where_sql:
            cost_where = f"{where_sql} AND cost IS NOT NULL"
            return_where = f"{where_sql} AND projected_return IS NOT NULL"
        else:
            cost_where = "WHERE cost IS NOT NULL"
            return_where = "WHERE projected_return IS NOT NULL"

        cost_count = conn.execute(
            f"SELECT COUNT(*) as cnt FROM contracts {cost_where}", params
        ).fetchone()["cnt"]

        return_count = conn.execute(
            f"SELECT COUNT(*) as cnt FROM contracts {return_where}", params
        ).fetchone()["cnt"]

        # Use MIN() to get a deterministic representative value per initiative
        cost_by_initiative: dict[str, str] = {}
        for row in conn.execute(
            f"SELECT initiative, MIN(cost) as cost FROM contracts {cost_where} GROUP BY initiative",
            params,
        ):
            cost_by_initiative[row["initiative"]] = row["cost"]

        return_by_initiative: dict[str, str] = {}
        for row in conn.execute(
            f"SELECT initiative, MIN(projected_return) as projected_return FROM contracts {return_where} GROUP BY initiative",
            params,
        ):
            return_by_initiative[row["initiative"]] = row["projected_return"]

        financial = FinancialMetrics(
            cost_coverage_count=cost_count,
            cost_coverage_percentage=round(cost_count / total * 100, 2) if total > 0 else 0.0,
            return_coverage_count=return_count,
            return_coverage_percentage=round(return_count / total * 100, 2) if total > 0 else 0.0,
            cost_by_initiative=cost_by_initiative,
            return_by_initiative=return_by_initiative,
        )

        # --- Cross-tabulations ---
        cross_area_initiative: list[CrossTabEntry] = []
        for row in conn.execute(
            f"SELECT area, initiative, COUNT(*) as cnt FROM contracts {where_sql} GROUP BY area, initiative",
            params,
        ):
            cross_area_initiative.append(
                CrossTabEntry(row=row["area"], col=row["initiative"], count=row["cnt"])
            )

        cross_area_status: list[CrossTabEntry] = []
        for row in conn.execute(
            f"SELECT area, status, COUNT(*) as cnt FROM contracts {where_sql} GROUP BY area, status",
            params,
        ):
            cross_area_status.append(
                CrossTabEntry(row=row["area"], col=row["status"], count=row["cnt"])
            )

        # --- Filter options (always unfiltered) ---
        areas = [r["area"] for r in conn.execute("SELECT DISTINCT area FROM contracts")]
        initiatives = [r["initiative"] for r in conn.execute("SELECT DISTINCT initiative FROM contracts")]
        statuses = [r["status"] for r in conn.execute("SELECT DISTINCT status FROM contracts")]
        owners = [r["owner"] for r in conn.execute("SELECT DISTINCT owner FROM contracts")]

        filter_options = FilterOptions(
            areas=areas,
            initiatives=initiatives,
            statuses=statuses,
            owners=owners,
        )

        return ExecutiveDashboardReport(
            total_contracts=total,
            by_status=by_status,
            by_initiative=by_initiative,
            by_area=by_area,
            by_owner=by_owner,
            compliance=compliance,
            financial=financial,
            cross_area_initiative=cross_area_initiative,
            cross_area_status=cross_area_status,
            filter_options=filter_options,
        )
    finally:
        conn.close()

