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
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    issue TEXT NOT NULL,
    priority_score INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection() -> sqlite3.Connection:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA)
        count = connection.execute(
            "SELECT COUNT(*) AS count FROM citizen_requests"
        ).fetchone()["count"]
        if count:
            return

        seed_path = Path(__file__).resolve().parents[2] / "data" / "demo_requests.json"
        if not seed_path.exists():
            return

        seed_rows = json.loads(seed_path.read_text(encoding="utf-8"))
        connection.executemany(
            """
            INSERT INTO citizen_requests
              (text, language, category, location, issue, priority_score, status, created_at)
            VALUES
              (:text, :language, :category, :location, :issue, :priority_score, :status, :created_at)
            """,
            seed_rows,
        )


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()