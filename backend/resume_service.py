"""Persistent, user-scoped storage for generated resumes."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from backend.database import get_connection, initialize_database


def save_resume(user_id: int, resume: dict[str, Any], template_name: str) -> tuple[bool, str]:
    """Save one generated resume for the authenticated user."""
    if not isinstance(user_id, int) or user_id <= 0:
        return False, "Please sign in again before saving a resume."
    if not isinstance(resume, dict) or not resume:
        return False, "Generate a resume before saving it."

    # Provide useful labels even if the AI response is missing optional fields.
    display_name = str(resume.get("name") or "Untitled resume").strip()[:120]
    target_role = str(resume.get("target_role") or "Career resume").strip()[:120]
    template_name = str(template_name or "Classic ATS").strip()[:80]

    initialize_database()
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO saved_resumes
                    (user_id, display_name, target_role, template_name, resume_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, display_name, target_role, template_name, json.dumps(resume, ensure_ascii=False)),
            )
    except (sqlite3.DatabaseError, TypeError, ValueError):
        return False, "We could not save this resume. Please try again."

    return True, "Resume saved to My resumes."


def list_saved_resumes(user_id: int) -> list[dict[str, Any]]:
    """Return only the resume summaries owned by the current user."""
    if not isinstance(user_id, int) or user_id <= 0:
        return []

    initialize_database()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, display_name, target_role, template_name, created_at
            FROM saved_resumes
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_saved_resume(user_id: int, resume_id: int) -> dict[str, Any] | None:
    """Load one resume only when it belongs to the authenticated user."""
    if not isinstance(user_id, int) or user_id <= 0 or not isinstance(resume_id, int) or resume_id <= 0:
        return None

    initialize_database()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT resume_json FROM saved_resumes WHERE id = ? AND user_id = ?",
            (resume_id, user_id),
        ).fetchone()

    if row is None:
        return None
    try:
        resume = json.loads(row["resume_json"])
    except (json.JSONDecodeError, TypeError):
        return None
    return resume if isinstance(resume, dict) else None
