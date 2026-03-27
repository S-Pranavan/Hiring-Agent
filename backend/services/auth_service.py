from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sqlite3
import time
from typing import Any

from backend.core.config import settings
from backend.data.database import get_connection


ITERATIONS = 120_000
TOKEN_TTL_SECONDS = 60 * 60 * 8


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_text, salt_b64, digest_b64 = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = base64.b64decode(salt_b64.encode())
        expected = base64.b64decode(digest_b64.encode())
    except (ValueError, TypeError):
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padded = value + "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(padded.encode())


def _sign(value: str) -> str:
    return _base64url_encode(hmac.new(settings.secret_key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).digest())


def issue_access_token(user: dict[str, Any]) -> str:
    payload = {
        "sub": user["id"],
        "role": user["role"],
        "email": user["email"],
        "candidate_id": user.get("candidate_id"),
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    encoded_payload = _base64url_encode(json.dumps(payload).encode("utf-8"))
    return f"{encoded_payload}.{_sign(encoded_payload)}"


def verify_access_token(token: str) -> dict[str, Any] | None:
    try:
        encoded_payload, provided_signature = token.split(".", 1)
    except ValueError:
        return None
    expected_signature = _sign(encoded_payload)
    if not hmac.compare_digest(provided_signature, expected_signature):
        return None
    try:
        payload = json.loads(_base64url_decode(encoded_payload).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return None
    if payload.get("exp", 0) < int(time.time()):
        return None
    user = get_user_by_id(int(payload["sub"]))
    if not user or not user["is_active"]:
        return None
    return user


def _row_to_user(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "role": row["role"],
        "candidate_id": row["candidate_id"],
        "is_active": bool(row["is_active"]),
    }


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT id, full_name, email, role, candidate_id, is_active FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_user(row)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT id, full_name, email, role, candidate_id, is_active FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
    return _row_to_user(row)


def authenticate_user(email: str, password: str, role: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE lower(email) = lower(?) AND role = ?", (email, role)).fetchone()
    if row is None or not row["is_active"]:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return _row_to_user(row)


def register_candidate_user(full_name: str, email: str, password: str, phone: str | None = None, summary: str | None = None) -> dict[str, Any]:
    existing = get_user_by_email(email)
    if existing:
        raise ValueError("An account with this email already exists")

    password_hash = hash_password(password)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO candidates (full_name, email, phone, role, job_id, status, match_score, soft_skills, ego, interview_score, fraud_risk, timeline_json, linkedin_url, cover_letter, cv_file_path, cv_file_name, cv_file_type, cv_file_size)
            VALUES (?, ?, ?, 'Candidate', 'general-candidate-pool', 'registered', 'Pending', 'Pending', 'Pending', 'Pending', 'Pending', ?, '', ?, '', '', '', 0)
            """,
            (
                full_name,
                email,
                phone or "",
                '[{"stage": "Account created", "status": "Completed", "date": "Today", "detail": "Candidate account created successfully."}]',
                summary or "",
            ),
        )
        candidate_id = int(cursor.lastrowid)
        profile = {
            "candidate": {"id": candidate_id, "full_name": full_name, "email": email, "status": "registered", "job_id": "general-candidate-pool"},
            "structured_cv": {"summary": summary or "", "skills": [], "highlights": [], "source_file": None},
            "cv_matching": None,
            "soft_skills": None,
            "ego_text": None,
            "final_score": None,
            "agent_status": {"screening": "pending", "soft_skills": "pending", "ego": "pending", "scheduling": "pending", "interview": "pending", "video_analysis": "pending", "answer_evaluation": "pending"},
        }
        connection.execute("INSERT INTO candidate_profiles (candidate_id, profile_json) VALUES (?, ?)", (candidate_id, __import__('json').dumps(profile)))
        user_cursor = connection.execute(
            "INSERT INTO users (full_name, email, password_hash, role, candidate_id, is_active) VALUES (?, ?, ?, 'candidate', ?, 1)",
            (full_name, email, password_hash, candidate_id),
        )
        user_id = int(user_cursor.lastrowid)
        connection.commit()
    return {"id": user_id, "full_name": full_name, "email": email, "role": "candidate", "candidate_id": candidate_id, "is_active": True}
