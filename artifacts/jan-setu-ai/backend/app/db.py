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
    location TEXT NOT NULL,
    issue TEXT NOT NULL,
    urgency TEXT NOT NULL DEFAULT 'Monitor',
    severity TEXT NOT NULL DEFAULT 'Low',
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
        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(citizen_requests)").fetchall()
        }
        migrations = {
            "translated_text": "ALTER TABLE citizen_requests ADD COLUMN translated_text TEXT NOT NULL DEFAULT ''",
            "understanding": "ALTER TABLE citizen_requests ADD COLUMN understanding TEXT NOT NULL DEFAULT ''",
            "urgency": "ALTER TABLE citizen_requests ADD COLUMN urgency TEXT NOT NULL DEFAULT 'Monitor'",
            "severity": "ALTER TABLE citizen_requests ADD COLUMN severity TEXT NOT NULL DEFAULT 'Low'",
        }
        for column, statement in migrations.items():
            if column not in existing_columns:
                connection.execute(statement)
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