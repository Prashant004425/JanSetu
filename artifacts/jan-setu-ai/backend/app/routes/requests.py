from datetime import datetime
import sqlite3

from fastapi import APIRouter, Depends, Query

from ..db import get_db
from ..schemas import (
    CitizenRequest,
    CitizenRequestInput,
    DashboardSummary,
    RequestAnalysis,
)
from ..services.ai import analyze_request


router = APIRouter(prefix="/requests", tags=["citizen requests"])


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
    return CitizenRequest(
        id=row["id"],
        text=row["text"],
        location=row["location"],
        language=row["language"],
        translated_text=details["translated_text"],
        understanding=details["understanding"],
        categories=categories,
        category=category,
        issue=row["issue"],
        urgency=details["urgency"],
        severity=details["severity"],
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
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
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
    analysis = analyze_request(payload.text, payload.location)
    similar_count = connection.execute(
        "SELECT COUNT(*) AS count FROM citizen_requests WHERE category = ? OR location = ?",
        (analysis["category"], analysis["location"]),
    ).fetchone()["count"]
    cursor = connection.execute(
        """
        INSERT INTO citizen_requests
          (text, language, translated_text, understanding, category, location, issue,
          urgency, severity, confidence, priority_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
        """,
        (
            payload.text,
            analysis["language"],
            analysis["translated_text"],
            analysis["understanding"],
            analysis["category"],
            analysis["location"],
            analysis["issue"],
            analysis["urgency"],
            analysis["severity"],
            analysis["confidence"],
            analysis["priority_score"],
        ),
    )
    connection.commit()
    row = connection.execute(
        "SELECT * FROM citizen_requests WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    result = row_to_request(row)
    return result.model_copy(update={"similar_request_count": similar_count})


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