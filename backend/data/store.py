from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Callable

from backend.data.database import get_connection


JsonDict = dict[str, Any]


def _loads(value: str | None, default: Any) -> Any:
    if not value:
        return deepcopy(default)
    return json.loads(value)


def _job_from_row(row) -> JsonDict:
    return {
        "id": row["id"],
        "title": row["title"],
        "location": row["location"],
        "type": row["type"],
        "department": row["department"],
        "experience": row["experience"],
        "summary": row["summary"],
        "description": _loads(row["description_json"], []),
        "requirements": _loads(row["requirements_json"], []),
        "responsibilities": _loads(row["responsibilities_json"], []),
        "skills": _loads(row["skills_json"], []),
        "salary": row["salary"],
        "status": row["status"],
    }


def _application_from_row(row) -> JsonDict:
    return {
        "id": row["id"],
        "candidate": row["full_name"],
        "email": row["email"],
        "phone": row["phone"] or "",
        "role": row["role"],
        "job_id": row["job_id"],
        "status": row["status"],
        "match_score": row["match_score"],
        "soft_skills": row["soft_skills"],
        "ego": row["ego"],
        "interview_score": row["interview_score"],
        "fraud_risk": row["fraud_risk"],
        "timeline": _loads(row["timeline_json"], []),
        "cv_file_path": row["cv_file_path"] or None,
        "cv_file_name": row["cv_file_name"] or None,
        "cv_file_type": row["cv_file_type"] or None,
        "cv_file_size": row["cv_file_size"] or 0,
    }


def list_jobs() -> list[JsonDict]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM jobs ORDER BY title ASC").fetchall()
    return [_job_from_row(row) for row in rows]


def get_job(job_id: str) -> JsonDict | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _job_from_row(row) if row else None


def list_metrics(role: str) -> list[JsonDict]:
    with get_connection() as connection:
        rows = connection.execute("SELECT label, value, delta, tone FROM metrics WHERE role = ? ORDER BY id ASC", (role,)).fetchall()
        if not rows:
            rows = connection.execute("SELECT label, value, delta, tone FROM metrics WHERE role = 'candidate' ORDER BY id ASC").fetchall()
    return [dict(row) for row in rows]


def list_applications() -> list[JsonDict]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM candidates ORDER BY id DESC").fetchall()
    return [_application_from_row(row) for row in rows]


def get_user_applications(candidate_id: int | None) -> list[JsonDict]:
    if candidate_id is None:
        return []
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM candidates WHERE id = ? ORDER BY id DESC", (candidate_id,)).fetchall()
    return [_application_from_row(row) for row in rows]


def get_application(application_id: int) -> JsonDict | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM candidates WHERE id = ?", (application_id,)).fetchone()
    return _application_from_row(row) if row else None


def create_application(payload: JsonDict) -> JsonDict:
    timeline = [
        {"stage": "Application submitted", "status": "Completed", "date": datetime.utcnow().strftime("%b %d"), "detail": "Application received through the portal."},
        {"stage": "AI screening", "status": "In progress", "date": datetime.utcnow().strftime("%b %d"), "detail": "Local agent workflow is evaluating the application."},
    ]
    with get_connection() as connection:
        job = connection.execute("SELECT title FROM jobs WHERE id = ?", (payload["job_id"],)).fetchone()
        role_title = job["title"] if job else payload["role"]
        cursor = connection.execute(
            """
            INSERT INTO candidates (full_name, email, phone, role, job_id, status, match_score, soft_skills, ego, interview_score, fraud_risk, timeline_json, linkedin_url, cover_letter, cv_file_path, cv_file_name, cv_file_type, cv_file_size)
            VALUES (?, ?, ?, ?, ?, 'received', 'Pending', 'Pending', 'Pending', 'Pending', 'Pending', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["full_name"], payload["email"], payload.get("phone", ""), role_title, payload["job_id"], json.dumps(timeline), payload.get("linkedin_url", ""), payload.get("cover_letter", ""),
                payload.get("cv_file_path", ""), payload.get("cv_file_name", ""), payload.get("cv_file_type", ""), payload.get("cv_file_size", 0),
            ),
        )
        candidate_id = int(cursor.lastrowid)
        profile = {
            "candidate": {"id": candidate_id, "full_name": payload["full_name"], "email": payload["email"], "status": "received", "job_id": payload["job_id"]},
            "structured_cv": {
                "summary": payload.get("cover_letter") or "Profile received.",
                "skills": [],
                "highlights": ([f"Uploaded CV: {payload['cv_file_name']}"] if payload.get("cv_file_name") else []),
                "source_file": payload.get("cv_file_name"),
            },
            "cv_matching": None,
            "soft_skills": None,
            "ego_text": None,
            "final_score": None,
            "agent_status": {"screening": "pending", "soft_skills": "pending", "ego": "pending", "scheduling": "pending", "interview": "pending", "video_analysis": "pending", "answer_evaluation": "pending"},
        }
        connection.execute("INSERT INTO candidate_profiles (candidate_id, profile_json) VALUES (?, ?)", (candidate_id, json.dumps(profile)))
        connection.execute("INSERT INTO notifications (candidate_id, title, body, tag) VALUES (?, ?, ?, ?)", (candidate_id, "Application received", f"Your application for {role_title} was submitted successfully.", "Application"))
        connection.execute("INSERT INTO interview_sessions (candidate_id, session_json) VALUES (?, ?)", (candidate_id, json.dumps({"session_id": f"session-{candidate_id}", "candidate_id": candidate_id, "job_id": payload["job_id"], "status": "pending", "current_question": 1, "questions": [], "answers": [], "evaluation": None, "fraud_analysis": None})))
        connection.commit()
    return get_application(candidate_id)  # type: ignore[return-value]


def update_application(application_id: int, updater: Callable[[JsonDict], None]) -> JsonDict | None:
    current = get_application(application_id)
    if not current:
        return None
    updater(current)
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE candidates
            SET status = ?, match_score = ?, soft_skills = ?, ego = ?, interview_score = ?, fraud_risk = ?, timeline_json = ?, cv_file_name = ?, cv_file_type = ?, cv_file_size = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                current["status"], current["match_score"], current["soft_skills"], current["ego"], current["interview_score"], current["fraud_risk"], json.dumps(current["timeline"]), current.get("cv_file_name"), current.get("cv_file_type"), current.get("cv_file_size", 0), application_id,
            ),
        )
        connection.commit()
    return get_application(application_id)


def set_candidate_profile(candidate_id: int, profile: JsonDict) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO candidate_profiles (candidate_id, profile_json) VALUES (?, ?) ON CONFLICT(candidate_id) DO UPDATE SET profile_json = excluded.profile_json, updated_at = CURRENT_TIMESTAMP",
            (candidate_id, json.dumps(profile)),
        )
        connection.commit()


def get_candidate_profile(candidate_id: int) -> JsonDict | None:
    with get_connection() as connection:
        row = connection.execute("SELECT profile_json FROM candidate_profiles WHERE candidate_id = ?", (candidate_id,)).fetchone()
    return _loads(row["profile_json"], None) if row else None


def add_notification(candidate_id: int, item: JsonDict) -> None:
    with get_connection() as connection:
        connection.execute("INSERT INTO notifications (candidate_id, title, body, tag) VALUES (?, ?, ?, ?)", (candidate_id, item["title"], item["body"], item["tag"]))
        connection.commit()


def get_notifications(candidate_id: int) -> list[JsonDict]:
    with get_connection() as connection:
        rows = connection.execute("SELECT title, body, tag FROM notifications WHERE candidate_id = ? ORDER BY id DESC", (candidate_id,)).fetchall()
    return [dict(row) for row in rows]


def set_interviews(candidate_id: int, items: list[JsonDict]) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM interviews WHERE candidate_id = ?", (candidate_id,))
        connection.executemany("INSERT INTO interviews (candidate_id, type, date, mode, status) VALUES (?, ?, ?, ?, ?)", [(candidate_id, item["type"], item["date"], item["mode"], item["status"]) for item in items])
        connection.commit()


def get_interviews(candidate_id: int) -> list[JsonDict]:
    with get_connection() as connection:
        rows = connection.execute("SELECT type, date, mode, status FROM interviews WHERE candidate_id = ? ORDER BY id ASC", (candidate_id,)).fetchall()
    return [dict(row) for row in rows]


def set_interview_session(candidate_id: int, session: JsonDict) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO interview_sessions (candidate_id, session_json) VALUES (?, ?) ON CONFLICT(candidate_id) DO UPDATE SET session_json = excluded.session_json, updated_at = CURRENT_TIMESTAMP",
            (candidate_id, json.dumps(session)),
        )
        connection.commit()


def get_interview_session(candidate_id: int) -> JsonDict | None:
    with get_connection() as connection:
        row = connection.execute("SELECT session_json FROM interview_sessions WHERE candidate_id = ?", (candidate_id,)).fetchone()
    return _loads(row["session_json"], None) if row else None


def get_dashboard_summary() -> JsonDict:
    applications = list_applications()
    shortlisted = 0
    interviewed = 0
    selected = 0
    fraud_alerts = 0
    for application in applications:
        status = application["status"].lower()
        if status in {"shortlisted", "scheduled", "interview_completed", "selected", "direct_join", "physical_interview_required"}:
            shortlisted += 1
        if status in {"interview_completed", "selected", "direct_join", "physical_interview_required"}:
            interviewed += 1
        if status in {"selected", "direct_join"}:
            selected += 1
        if application["fraud_risk"].lower() in {"moderate", "high"}:
            fraud_alerts += 1
    return {"received": len(applications), "shortlisted": shortlisted, "interviewed": interviewed, "selected": selected, "fraud_alerts": fraud_alerts}


def log_communication(candidate_id: int | None, channel: str, direction: str, subject: str | None, body: str | None, status: str, provider: str, metadata: JsonDict | None = None) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO communications (candidate_id, channel, direction, subject, body, status, provider, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (candidate_id, channel, direction, subject, body, status, provider, json.dumps(metadata or {})),
        )
        connection.commit()


def list_communications(limit: int = 50) -> list[JsonDict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                communications.id,
                communications.candidate_id,
                communications.channel,
                communications.direction,
                communications.subject,
                communications.body,
                communications.status,
                communications.provider,
                communications.metadata_json,
                communications.created_at,
                candidates.full_name
            FROM communications
            LEFT JOIN candidates ON candidates.id = communications.candidate_id
            ORDER BY communications.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    items: list[JsonDict] = []
    for row in rows:
        metadata = _loads(row["metadata_json"], {})
        items.append(
            {
                "id": row["id"],
                "candidate_id": row["candidate_id"],
                "candidate_name": row["full_name"] or "System",
                "channel": row["channel"],
                "direction": row["direction"],
                "subject": row["subject"] or "",
                "body": row["body"] or "",
                "status": row["status"],
                "provider": row["provider"] or "unknown",
                "created_at": row["created_at"],
                "metadata": metadata,
                "recipient": metadata.get("recipient", ""),
            }
        )
    return items


def record_decision(payload: JsonDict, decision_type: str) -> JsonDict:
    decision = {"decision_type": decision_type, **payload}
    with get_connection() as connection:
        connection.execute("INSERT INTO decisions (candidate_id, job_id, decision_type, payload_json) VALUES (?, ?, ?, ?)", (payload["candidate_id"], payload["job_id"], decision_type, json.dumps(payload)))
        connection.commit()

    status_map = {"direct_hire": "direct_join", "physical_interview": "physical_interview_required", "reject": "rejected", "shortlist": "shortlisted", "select": "selected"}
    label_map = {"direct_hire": "direct hire", "physical_interview": "physical interview", "reject": "rejected", "shortlist": "shortlisted", "select": "selected"}
    new_status = status_map.get(decision_type, decision_type)
    label = label_map.get(decision_type, decision_type.replace("_", " "))

    def _apply(application: JsonDict) -> None:
        application["status"] = new_status
        if decision_type in {"select", "direct_hire"} and application["interview_score"] == "Pending":
            application["interview_score"] = "Approved"
        application["timeline"].append({"stage": "Final decision", "status": "Completed", "date": datetime.utcnow().strftime("%b %d"), "detail": f"Decision recorded: {label}."})

    update_application(payload["candidate_id"], _apply)
    profile = get_candidate_profile(payload["candidate_id"])
    if profile:
        profile["candidate"]["status"] = new_status
        if profile.get("final_score"):
            profile["final_score"]["recommendation"] = label.replace(" ", "_")
        set_candidate_profile(payload["candidate_id"], profile)
    add_notification(payload["candidate_id"], {"title": "Decision update", "body": f"A hiring decision has been recorded: {label}.", "tag": "Decision"})
    log_communication(payload["candidate_id"], "system", "outbound", "Decision update", f"Decision recorded: {label}", "recorded", "local-system", {"decision_type": decision_type})
    return deepcopy(decision)
