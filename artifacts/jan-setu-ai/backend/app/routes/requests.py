from datetime import datetime, timezone
import logging
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db import get_db
from ..schemas import (
    CitizenRequest,
    CitizenRequestInput,
    DashboardSummary,
    RequestAnalysis,
    RequestStatusUpdate,
)
from ..services.ai import analyze_request, normalize_urgency


router = APIRouter(prefix="/requests", tags=["citizen requests"])
logger = logging.getLogger(__name__)


def row_to_request(row: sqlite3.Row) -> CitizenRequest:
    has_stored_analysis = bool(
        row["understanding"] if "understanding" in row.keys() else ""
    )
    stored_analysis = {
        "translated_text": row["translated_text"] if has_stored_analysis else "",
        "understanding": row["understanding"] if has_stored_analysis else "",
        "urgency": row["urgency"] if has_stored_analysis else "",
        "severity": row["severity"] if has_stored_analysis else "",
    }
    derived_analysis = (
        analyze_request(row["text"], row["location"])
        if not stored_analysis["understanding"]
        else {}
    )
    details = {
        **derived_analysis,
        **{key: value for key, value in stored_analysis.items() if value},
    }
    categories = (
        derived_analysis.get("categories")
        or row["category"].split(" + ")
    )
    category = str(derived_analysis.get("category") or row["category"])
    subcategory = str(derived_analysis.get("subcategory") or (row["subcategory"] if "subcategory" in row.keys() else "General civic need"))
    urgency = normalize_urgency(details["urgency"])
    severity = normalize_urgency(details["severity"])
    return CitizenRequest(
        id=row["id"],
        request_id=(row["request_id"] if "request_id" in row.keys() and row["request_id"] else f"REQ-{row['id']:04d}"),
        text=row["text"],
        location=row["location"] or None,
        language=row["language"],
        translated_text=details["translated_text"],
        understanding=details["understanding"],
        categories=categories,
        category=category,
        subcategory=subcategory,
        issue=row["issue"],
        urgency=urgency,
        severity=severity,
        confidence=float(row["confidence"]) if "confidence" in row.keys() else 0.86,
        priority_score=row["priority_score"],
        priority_label=(
            "High priority"
            if row["priority_score"] >= 75
            else "Needs review"
            if row["priority_score"] >= 55
            else "Monitor"
        ),
        similar_request_count=0,
        status="pending" if row["status"] == "new" else row["status"],
        risk_level=row["risk_level"] if "risk_level" in row.keys() and row["risk_level"] else "LOW",
        assigned_to=row["assigned_to"] if "assigned_to" in row.keys() else None,
        progress_percent=int(row["progress_percent"] or 0) if "progress_percent" in row.keys() else 0,
        government_notes=row["government_notes"] if "government_notes" in row.keys() and row["government_notes"] else "",
        completion_notes=row["completion_notes"] if "completion_notes" in row.keys() and row["completion_notes"] else "",
        completed_at=datetime.fromisoformat(row["completed_at"]) if "completed_at" in row.keys() and row["completed_at"] else None,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]) if "updated_at" in row.keys() else datetime.fromisoformat(row["created_at"]),
    )


@router.get("", response_model=list[CitizenRequest])
def list_requests(
    limit: int = Query(default=20, ge=1, le=100),
    connection: sqlite3.Connection = Depends(get_db),
) -> list[CitizenRequest]:
    rows = connection.execute(
        "SELECT * FROM citizen_requests ORDER BY datetime(created_at) DESC, id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    requests = []
    for row in rows:
        result = row_to_request(row)
        similar_count = connection.execute(
            "SELECT COUNT(*) AS count FROM citizen_requests WHERE id != ? AND (category = ? OR location = ?)",
            (row["id"], row["category"], row["location"]),
        ).fetchone()["count"]
        requests.append(result.model_copy(update={"similar_request_count": similar_count}))
    return requests


@router.post("/analyze", response_model=CitizenRequest, status_code=201)
def create_and_analyze_request(
    payload: CitizenRequestInput,
    connection: sqlite3.Connection = Depends(get_db),
) -> CitizenRequest:
    logger.info("Citizen request received: database=%s", connection.execute("PRAGMA database_list").fetchone()["file"])
    analysis = analyze_request(payload.text, payload.location)
    created_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    similar_count = connection.execute(
        "SELECT COUNT(*) AS count FROM citizen_requests WHERE category = ? OR location = ?",
        (analysis["category"], analysis["location"]),
    ).fetchone()["count"]
    try:
        cursor = connection.execute(
            """
            INSERT INTO citizen_requests
              (text, language, translated_text, understanding, category, subcategory, location, issue,
              urgency, severity, confidence, priority_score, status, created_at, updated_at,
              original_text, original_language, english_translation, village, district)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.text,
                analysis["language"],
                analysis["translated_text"],
                analysis["understanding"],
                analysis["category"],
                analysis["subcategory"],
                analysis["location"] or "",
                analysis["issue"],
                analysis["urgency"],
                analysis["severity"],
                analysis["confidence"],
                analysis["priority_score"],
                created_at,
                created_at,
                payload.text,
                analysis["language"],
                analysis["translated_text"],
                analysis["location"] or "",
                "",
            ),
        )
        connection.execute(
            "UPDATE citizen_requests SET request_id = 'REQ-' || printf('%04d', id) "
            "WHERE id = ?",
            (cursor.lastrowid,),
        )
        connection.commit()
        logger.info("Citizen request committed: id=%s", cursor.lastrowid)
    except sqlite3.Error as error:
        connection.rollback()
        raise HTTPException(
            status_code=503,
            detail={"success": False, "error": "Database insertion failed", "detail": str(error)},
        ) from error
    row = connection.execute(
        "SELECT * FROM citizen_requests WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    result = row_to_request(row)
    return result.model_copy(update={"similar_request_count": similar_count})


@router.patch("/{request_id}/status", response_model=CitizenRequest)
def update_request_status(
    request_id: int,
    payload: RequestStatusUpdate,
    connection: sqlite3.Connection = Depends(get_db),
) -> CitizenRequest:
    allowed_statuses = {"pending", "under_review", "approved", "in_progress", "completed", "rejected"}
    status = payload.status.strip().lower().replace(" ", "_")
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(sorted(allowed_statuses))}.")
    cursor = connection.execute(
        "UPDATE citizen_requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, request_id),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Citizen request not found.")
    connection.commit()
    row = connection.execute("SELECT * FROM citizen_requests WHERE id = ?", (request_id,)).fetchone()
    return row_to_request(row)


@router.post("/preview", response_model=RequestAnalysis)
def preview_analysis(payload: CitizenRequestInput) -> RequestAnalysis:
    return RequestAnalysis(
        **analyze_request(payload.text, payload.location),
        similar_request_count=0,
    )


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    connection: sqlite3.Connection = Depends(get_db),
) -> DashboardSummary:
    total = connection.execute(
        "SELECT COUNT(*) AS count FROM citizen_requests"
    ).fetchone()["count"]
    completed = connection.execute(
        "SELECT COUNT(*) AS count FROM citizen_requests WHERE status = 'completed'"
    ).fetchone()["count"]
    pending = total - completed
    high_priority = connection.execute(
        "SELECT COUNT(*) AS count FROM citizen_requests WHERE priority_score >= 75"
    ).fetchone()["count"]
    categories = connection.execute(
        """
        SELECT category, COUNT(*) AS count
        FROM citizen_requests
        GROUP BY category
        ORDER BY count DESC, category ASC
        LIMIT 1
        """
    ).fetchone()
    locations = connection.execute(
        """
        SELECT location, COUNT(*) AS count
        FROM citizen_requests
        GROUP BY location
        ORDER BY count DESC, location ASC
        LIMIT 1
        """
    ).fetchone()
    return DashboardSummary(
        total_requests=total,
        completed_requests=completed,
        pending_requests=pending,
        high_priority_requests=high_priority,
        active_hotspots=max(1, min(3, high_priority)) if total else 0,
        top_category=categories["category"] if categories else "No data",
        top_location=locations["location"] if locations else "No data",
    )