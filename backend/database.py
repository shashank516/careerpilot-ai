"""SQLite database setup for Pathway AI."""

from __future__ import annotations

import sqlite3
from pathlib import Path


# Store the local database outside the UI and service code.
DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "pathway_ai.db"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection that exposes rows by column name."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the tables required by the application when they do not exist."""
    with get_connection() as connection:
        # Email is unique so a person can create only one account per address.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Every saved resume belongs to exactly one signed-in user.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                display_name TEXT NOT NULL,
                target_role TEXT NOT NULL,
                template_name TEXT NOT NULL,
                resume_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
