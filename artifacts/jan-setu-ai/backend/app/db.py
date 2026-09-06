from collections.abc import Generator
import json
import sqlite3
from pathlib import Path

from .config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS citizen_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    language TEXT NOT NULL,
    translated_text TEXT NOT NULL DEFAULT '',
    understanding TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL DEFAULT 'General civic need',
    location TEXT NOT NULL,
    issue TEXT NOT NULL,
    urgency TEXT NOT NULL DEFAULT 'Monitor',
    severity TEXT NOT NULL DEFAULT 'Low',
    confidence REAL NOT NULL DEFAULT 0.86 CHECK (confidence >= 0 AND confidence <= 1),
    priority_score INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS work_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    previous_status TEXT,
    new_status TEXT,
    previous_progress INTEGER NOT NULL DEFAULT 0,
    new_progress INTEGER NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT '',
    updated_by TEXT NOT NULL DEFAULT 'Prototype government user',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES citizen_requests(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_citizen_requests_priority
    ON citizen_requests(priority_score DESC, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_citizen_requests_category
    ON citizen_requests(category);
CREATE INDEX IF NOT EXISTS idx_citizen_requests_location
    ON citizen_requests(location);
"""


def get_connection() -> sqlite3.Connection:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA)
        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(citizen_requests)").fetchall()
        }
        migrations = {
            "translated_text": "ALTER TABLE citizen_requests ADD COLUMN translated_text TEXT NOT NULL DEFAULT ''",
            "understanding": "ALTER TABLE citizen_requests ADD COLUMN understanding TEXT NOT NULL DEFAULT ''",
            "urgency": "ALTER TABLE citizen_requests ADD COLUMN urgency TEXT NOT NULL DEFAULT 'Monitor'",
            "severity": "ALTER TABLE citizen_requests ADD COLUMN severity TEXT NOT NULL DEFAULT 'Low'",
            "confidence": "ALTER TABLE citizen_requests ADD COLUMN confidence REAL NOT NULL DEFAULT 0.86",
            "updated_at": "ALTER TABLE citizen_requests ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''",
            "subcategory": "ALTER TABLE citizen_requests ADD COLUMN subcategory TEXT NOT NULL DEFAULT 'General civic need'",
            "request_id": "ALTER TABLE citizen_requests ADD COLUMN request_id TEXT",
            "user_id": "ALTER TABLE citizen_requests ADD COLUMN user_id TEXT",
            "original_text": "ALTER TABLE citizen_requests ADD COLUMN original_text TEXT",
            "original_language": "ALTER TABLE citizen_requests ADD COLUMN original_language TEXT",
            "english_translation": "ALTER TABLE citizen_requests ADD COLUMN english_translation TEXT",
            "village": "ALTER TABLE citizen_requests ADD COLUMN village TEXT",
            "district": "ALTER TABLE citizen_requests ADD COLUMN district TEXT",
            "latitude": "ALTER TABLE citizen_requests ADD COLUMN latitude REAL",
            "longitude": "ALTER TABLE citizen_requests ADD COLUMN longitude REAL",
            "risk_level": "ALTER TABLE citizen_requests ADD COLUMN risk_level TEXT NOT NULL DEFAULT 'LOW'",
            "assigned_to": "ALTER TABLE citizen_requests ADD COLUMN assigned_to TEXT",
            "progress_percent": "ALTER TABLE citizen_requests ADD COLUMN progress_percent INTEGER NOT NULL DEFAULT 0",
            "government_notes": "ALTER TABLE citizen_requests ADD COLUMN government_notes TEXT NOT NULL DEFAULT ''",
            "completion_notes": "ALTER TABLE citizen_requests ADD COLUMN completion_notes TEXT NOT NULL DEFAULT ''",
            "completed_at": "ALTER TABLE citizen_requests ADD COLUMN completed_at TEXT",
        }
        for column, statement in migrations.items():
            if column not in existing_columns:
                connection.execute(statement)
        connection.execute(
            "UPDATE citizen_requests SET updated_at = created_at "
            "WHERE updated_at IS NULL OR updated_at = ''"
        )
        connection.execute(
            "UPDATE citizen_requests SET request_id = 'REQ-' || printf('%04d', id) "
            "WHERE request_id IS NULL OR request_id = ''"
        )
        connection.execute(
            "UPDATE citizen_requests SET original_text = text, original_language = language, "
            "english_translation = translated_text WHERE original_text IS NULL"
        )
        connection.execute(
            "UPDATE citizen_requests SET risk_level = CASE "
            "WHEN priority_score >= 85 OR (urgency IN ('HIGH','Immediate') AND severity IN ('HIGH','High')) THEN 'CRITICAL' "
            "WHEN priority_score >= 70 OR urgency IN ('HIGH','Immediate') OR severity IN ('HIGH','High') THEN 'HIGH' "
            "WHEN priority_score >= 50 THEN 'MEDIUM' ELSE 'LOW' END"
        )
        connection.execute(
            "UPDATE citizen_requests SET status = 'pending' WHERE status = 'new'"
        )
        count = connection.execute(
            "SELECT COUNT(*) AS count FROM citizen_requests"
        ).fetchone()["count"]
        seed_path = Path(__file__).resolve().parents[2] / "data" / "demo_requests.json"
        if not seed_path.exists():
            return

        seed_rows = json.loads(seed_path.read_text(encoding="utf-8"))
        existing_texts = {
            row["text"]
            for row in connection.execute("SELECT text FROM citizen_requests").fetchall()
        }
        new_seed_rows = [row for row in seed_rows if row["text"] not in existing_texts]
        if new_seed_rows:
            connection.executemany(
                """
                INSERT INTO citizen_requests
                  (text, language, category, location, issue, priority_score, status, created_at)
                VALUES
                  (:text, :language, :category, :location, :issue, :priority_score, :status, :created_at)
                """,
                new_seed_rows,
            )


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()