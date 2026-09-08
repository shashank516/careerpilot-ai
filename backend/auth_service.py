"""Authentication business logic kept separate from the Streamlit interface."""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from typing import Any

from backend.database import get_connection, initialize_database


# PBKDF2 makes leaked passwords much harder to crack than plain-text storage.
HASH_ITERATIONS = 600_000


def _hash_password(password: str, salt: bytes | None = None) -> str:
    """Create a salted PBKDF2 password hash suitable for SQLite storage."""
    salt = salt or os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, HASH_ITERATIONS
    )
    return f"{salt.hex()}${password_hash.hex()}"


def _password_matches(password: str, stored_value: str) -> bool:
    """Safely compare a supplied password with its saved hash."""
    try:
        salt_hex, expected_hash = stored_value.split("$", maxsplit=1)
        actual_hash = _hash_password(password, bytes.fromhex(salt_hex)).split("$", maxsplit=1)[1]
        return hmac.compare_digest(actual_hash, expected_hash)
    except (ValueError, AttributeError):
        return False


def register_user(full_name: str, email: str, password: str) -> tuple[bool, str]:
    """Create an account after validating the values received from the UI."""
    full_name = full_name.strip()
    email = email.strip().lower()

    if len(full_name) < 2:
        return False, "Please enter your full name."
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        return False, "Please enter a valid email address."
    if len(password) < 8:
        return False, "Your password must contain at least 8 characters."

    initialize_database()
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, _hash_password(password)),
            )
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists. Please sign in."
    except sqlite3.DatabaseError:
        return False, "We could not create your account. Please try again."

    return True, "Account created. You can now sign in."


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    """Return safe user details when credentials are correct; otherwise None."""
    initialize_database()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, full_name, email, password_hash FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()

    if row is None or not _password_matches(password, row["password_hash"]):
        return None

    # Never pass the password hash to the Streamlit session state.
    return {"id": row["id"], "full_name": row["full_name"], "email": row["email"]}
