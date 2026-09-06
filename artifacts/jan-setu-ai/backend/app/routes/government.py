from datetime import datetime
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db import get_db
from ..schemas import (
    CitizenRequest,
    RequestStatusUpdate,
    WorkAssignmentUpdate,
    WorkProgressUpdate,
    WorkSummary,
)
from .requests import row_to_request

router = APIRouter(prefix="/government", tags=["government work management"])
VALID_STATUSES = {"pending", "in_progress", "on_hold", "completed", "cancelled"}


def risk_for(row: sqlite3.Row) -> str:
    urgency = str(row["urgency"]).upper()
    severity = str(row["severity"]).upper()
    score = int(row["priority_score"])
    if score >= 85 or (urgency == "HIGH" and severity == "HIGH"):
        return "CRITICAL"
    if score >= 70 or urgency == "HIGH" or severity == "HIGH":
        return "HIGH"
    if score >= 50 or urgency == "MEDIUM" or severity == "MEDIUM":
        return "MEDIUM"
    return "LOW"


def government_request(row: sqlite3.Row) -> CitizenRequest:
    result = row_to_request(row)
    return result.model_copy(update={
        "request_id": row["request_id"] or f"REQ-{row['id']:04d}",
        "status": "pending" if row["status"] == "new" else row["status"],
        "risk_level": row["risk_level"] or risk_for(row),
        "assigned_to": row["assigned_to"],
        "progress_percent": int(row["progress_percent"] or 0),
        "government_notes": row["government_notes"] or "",
        "completion_notes": row["completion_notes"] or "",
        "completed_at": datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
    })


def fetch_row(connection: sqlite3.Connection, request_id: int) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM citizen_requests WHERE id = ?", (request_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Work request not found.")
    return row


def record_update(
    connection: sqlite3.Connection,
    request_id: int,
    previous_status: str,
    new_status: str,
    previous_progress: int,
    new_progress: int,
    note: str,
) -> None:
    connection.execute(
        """
        INSERT INTO work_updates
          (request_id, previous_status, new_status, previous_progress, new_progress, note)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (request_id, previous_status, new_status, previous_progress, new_progress, note.strip()),
    )


@router.get("/requests", response_model=list[CitizenRequest])
def list_government_requests(
    status: str | None = Query(default=None),
    risk: str | None = Query(default=None),
    urgency: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=120),
    connection: sqlite3.Connection = Depends(get_db),
) -> list[CitizenRequest]:
    clauses: list[str] = []
    values: list[str] = []
    if status:
        clauses.append("status = ?")
        values.append(status.lower())
    if urgency:
        clauses.append("UPPER(urgency) = ?")
        values.append(urgency.upper())
    if search:
        term = f"%{search.casefold()}%"
        clauses.append("(LOWER(text) LIKE ? OR LOWER(category) LIKE ? OR LOWER(location) LIKE ? OR LOWER(request_id) LIKE ?)")
        values.extend([term, term, term, term])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = connection.execute(
        f"SELECT * FROM citizen_requests {where} ORDER BY created_at DESC, id DESC",
        values,
    ).fetchall()
    results = [government_request(row) for row in rows]
    return [item for item in results if not risk or item.risk_level == risk.upper()]


@router.get("/requests/{request_id}", response_model=CitizenRequest)
def get_government_request(
    request_id: int, connection: sqlite3.Connection = Depends(get_db)
) -> CitizenRequest:
    return government_request(fetch_row(connection, request_id))


@router.patch("/requests/{request_id}/status", response_model=CitizenRequest)
def update_government_status(
    request_id: int,
    payload: RequestStatusUpdate,
    connection: sqlite3.Connection = Depends(get_db),
) -> CitizenRequest:
    row = fetch_row(connection, request_id)
    status = payload.status.strip().lower().replace(" ", "_")
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}.")
    previous_status = "pending" if row["status"] == "new" else row["status"]
    previous_progress = int(row["progress_percent"] or 0)
    progress = 100 if status == "completed" else payload.progress_percent
    if status == "completed" and not payload.notes.strip():
        raise HTTPException(status_code=400, detail="Completion notes are required.")
    completed_at = "CURRENT_TIMESTAMP" if status == "completed" else "NULL"
    connection.execute(
        f"""
        UPDATE citizen_requests
        SET status = ?, progress_percent = ?, government_notes = ?,
            completion_notes = ?, completed_at = {completed_at},
            updated_at = CURRENT_TIMESTAMP, risk_level = ?
        WHERE id = ?
        """,
        (
            status,
            progress,
            payload.notes.strip(),
            payload.notes.strip() if status == "completed" else row["completion_notes"],
            risk_for(row),
            request_id,
        ),
    )
    record_update(connection, request_id, previous_status, status, previous_progress, progress, payload.notes)
    connection.commit()
    return government_request(fetch_row(connection, request_id))


@router.patch("/requests/{request_id}/progress", response_model=CitizenRequest)
def update_government_progress(
    request_id: int,
    payload: WorkProgressUpdate,
    connection: sqlite3.Connection = Depends(get_db),
) -> CitizenRequest:
    row = fetch_row(connection, request_id)
    previous_status = "pending" if row["status"] == "new" else row["status"]
    previous_progress = int(row["progress_percent"] or 0)
    status = "completed" if payload.progress_percent == 100 else (
        "in_progress" if previous_status in {"pending", "new"} else previous_status
    )
    if previous_status == "completed" and payload.progress_percent != 100:
        raise HTTPException(status_code=409, detail="Completed work must remain at 100% progress.")
    connection.execute(
        """
        UPDATE citizen_requests
        SET status = ?, progress_percent = ?, government_notes = ?,
            completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (status, payload.progress_percent, payload.notes.strip(), status, request_id),
    )
    record_update(connection, request_id, previous_status, status, previous_progress, payload.progress_percent, payload.notes)
    connection.commit()
    return government_request(fetch_row(connection, request_id))


@router.patch("/requests/{request_id}/assignment", response_model=CitizenRequest)
def update_assignment(
    request_id: int,
    payload: WorkAssignmentUpdate,
    connection: sqlite3.Connection = Depends(get_db),
) -> CitizenRequest:
    fetch_row(connection, request_id)
    connection.execute(
        "UPDATE citizen_requests SET assigned_to = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (payload.assigned_to.strip() if payload.assigned_to else None, request_id),
    )
    connection.commit()
    return government_request(fetch_row(connection, request_id))


@router.get("/requests/{request_id}/history")
def get_history(request_id: int, connection: sqlite3.Connection = Depends(get_db)):
    fetch_row(connection, request_id)
    return connection.execute(
        "SELECT * FROM work_updates WHERE request_id = ? ORDER BY datetime(created_at) DESC, id DESC",
        (request_id,),
    ).fetchall()


@router.get("/dashboard/summary", response_model=WorkSummary)
def government_summary(connection: sqlite3.Connection = Depends(get_db)) -> WorkSummary:
    row = connection.execute(
        """
        SELECT COUNT(*) total,
          SUM(CASE WHEN status IN ('new','pending') THEN 1 ELSE 0 END) pending,
          SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) in_progress,
          SUM(CASE WHEN status = 'on_hold' THEN 1 ELSE 0 END) on_hold,
          SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) completed,
          SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) cancelled,
          SUM(CASE WHEN UPPER(risk_level) IN ('HIGH','CRITICAL') THEN 1 ELSE 0 END) high_risk,
          SUM(CASE WHEN UPPER(risk_level) = 'CRITICAL' THEN 1 ELSE 0 END) critical_risk,
          SUM(CASE WHEN UPPER(urgency) = 'HIGH' THEN 1 ELSE 0 END) urgent,
          AVG(CASE WHEN completed_at IS NOT NULL THEN (julianday(completed_at) - julianday(created_at)) END) average_resolution_days
        FROM citizen_requests
        """
    ).fetchone()
    total = int(row["total"] or 0)
    completed = int(row["completed"] or 0)
    return WorkSummary(
        total=total,
        pending=int(row["pending"] or 0),
        in_progress=int(row["in_progress"] or 0),
        on_hold=int(row["on_hold"] or 0),
        completed=completed,
        cancelled=int(row["cancelled"] or 0),
        high_risk=int(row["high_risk"] or 0),
        critical_risk=int(row["critical_risk"] or 0),
        urgent=int(row["urgent"] or 0),
        completion_rate=round(completed / total * 100, 1) if total else 0,
        average_resolution_days=round(row["average_resolution_days"], 1) if row["average_resolution_days"] is not None else None,
    )
