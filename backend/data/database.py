from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from backend.core.config import settings


def _database_path() -> Path:
    raw_path = Path(settings.database_path)
    if raw_path.is_absolute():
        return raw_path
    return Path.cwd() / raw_path


def get_connection() -> sqlite3.Connection:
    db_path = _database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def _serialize(value: Any) -> str:
    return json.dumps(value)


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _seed_jobs(connection: sqlite3.Connection) -> None:
    existing = connection.execute("SELECT COUNT(*) AS count FROM jobs").fetchone()["count"]
    if existing:
        return

    jobs = [
        {
            "id": "ai-product-designer",
            "title": "AI Product Designer",
            "location": "Colombo, Sri Lanka",
            "type": "Hybrid",
            "department": "Product",
            "experience": "4+ years",
            "summary": "Design intuitive recruiting experiences for enterprise hiring teams and candidates.",
            "description": [
                "Lead UX strategy for AI-assisted recruiting workflows.",
                "Translate complex scoring into confident decision experiences.",
            ],
            "requirements": ["Portfolio with SaaS workflow design", "Design systems experience", "Research depth"],
            "responsibilities": [
                "Own candidate and reviewer journeys",
                "Partner with engineering and ML stakeholders",
                "Ship polished enterprise interfaces",
            ],
            "skills": ["Figma", "Design Systems", "User Research", "Product Thinking"],
            "salary": "$60k - $85k",
            "status": "Active",
        },
        {
            "id": "ml-recruiting-ops-lead",
            "title": "ML Recruiting Ops Lead",
            "location": "Remote",
            "type": "Full-time",
            "department": "Operations",
            "experience": "6+ years",
            "summary": "Operationalize AI screening, fraud monitoring, and interview quality assurance.",
            "description": [
                "Coordinate AI assessment pipelines across multiple hiring programs.",
                "Maintain recruiter trust with transparent QA and exception handling.",
            ],
            "requirements": ["Hiring operations leadership", "AI tooling familiarity", "Excellent analytics communication"],
            "responsibilities": ["Monitor workflows", "Review fraud signals", "Align decisions with hiring teams"],
            "skills": ["Analytics", "Recruiting Ops", "Stakeholder Management", "Process Design"],
            "salary": "$70k - $95k",
            "status": "Active",
        },
        {
            "id": "senior-full-stack-engineer",
            "title": "Senior Full-Stack Engineer",
            "location": "Singapore",
            "type": "Remote",
            "department": "Engineering",
            "experience": "5+ years",
            "summary": "Build the next generation of AI-assisted hiring infrastructure and portal workflows.",
            "description": [
                "Deliver reliable internal and candidate-facing experiences.",
                "Implement role-aware analytics, interview tooling, and decision workflows.",
            ],
            "requirements": ["Strong React and TypeScript", "API design", "Performance mindset"],
            "responsibilities": ["Build portal features", "Own APIs", "Collaborate with design and data teams"],
            "skills": ["Next.js", "TypeScript", "Node.js", "UX Engineering"],
            "salary": "$90k - $130k",
            "status": "Active",
        },
    ]

    metrics = {
        "candidate": [
            {"label": "Applications", "value": "12", "delta": "3 active", "tone": "brand"},
            {"label": "Interview invites", "value": "2", "delta": "1 this week", "tone": "success"},
            {"label": "Profile strength", "value": "89%", "delta": "Strong", "tone": "brand"},
            {"label": "Response time", "value": "< 24h", "delta": "Average", "tone": "success"},
        ],
        "admin": [
            {"label": "Open roles", "value": "26", "delta": "+4 this week", "tone": "brand"},
            {"label": "Applicants", "value": "1842", "delta": "+18%", "tone": "success"},
            {"label": "Fraud alerts", "value": "17", "delta": "Needs review", "tone": "warn"},
            {"label": "Offer ready", "value": "14", "delta": "High priority", "tone": "brand"},
        ],
        "hiring": [
            {"label": "Assigned roles", "value": "7", "delta": "2 urgent", "tone": "brand"},
            {"label": "Reviews pending", "value": "23", "delta": "Due today", "tone": "warn"},
            {"label": "Strong fit", "value": "11", "delta": "Top quartile", "tone": "success"},
            {"label": "Consensus ready", "value": "6", "delta": "Awaiting signoff", "tone": "brand"},
        ],
    }

    for job in jobs:
        connection.execute(
            """
            INSERT INTO jobs (id, title, location, type, department, experience, summary, description_json, requirements_json, responsibilities_json, skills_json, salary, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job["id"], job["title"], job["location"], job["type"], job["department"], job["experience"], job["summary"],
                _serialize(job["description"]), _serialize(job["requirements"]), _serialize(job["responsibilities"]), _serialize(job["skills"]), job["salary"], job["status"],
            ),
        )

    for role, items in metrics.items():
        for item in items:
            connection.execute("INSERT INTO metrics (role, label, value, delta, tone) VALUES (?, ?, ?, ?, ?)", (role, item["label"], item["value"], item.get("delta"), item.get("tone")))

    connection.execute(
        """
        INSERT INTO candidates (id, full_name, email, phone, role, job_id, status, match_score, soft_skills, ego, interview_score, fraud_risk, timeline_json, linkedin_url, cover_letter, cv_file_path, cv_file_name, cv_file_type, cv_file_size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1, "Ava Morgan", "ava@example.com", "+94 77 123 4567", "AI Product Designer", "ai-product-designer", "scheduled", "95%", "91%", "Low", "Pending", "Low",
            _serialize([
                {"stage": "Application submitted", "status": "Completed", "date": "Mar 21", "detail": "CV and portfolio received successfully."},
                {"stage": "AI screening", "status": "Completed", "date": "Mar 22", "detail": "Strong role fit, collaboration, and clarity signals."},
                {"stage": "Hiring review", "status": "Completed", "date": "Mar 24", "detail": "The hiring team approved the application for interview."},
                {"stage": "Interview scheduling", "status": "Completed", "date": "Mar 24", "detail": "AI interview invitation has been generated and sent."},
                {"stage": "AI interview", "status": "Upcoming", "date": "Mar 27", "detail": "Candidate can complete the interview from the portal."},
            ]),
            "https://linkedin.com/in/avamorgan",
            "Product designer focused on enterprise SaaS workflows, research-led design, and cross-functional collaboration.",
            "",
            "ava-morgan-portfolio.pdf",
            "application/pdf",
            0,
        ),
    )
    connection.execute(
        "INSERT INTO candidate_profiles (candidate_id, profile_json) VALUES (?, ?)",
        (
            1,
            _serialize(
                {
                    "candidate": {"id": 1, "full_name": "Ava Morgan", "email": "ava@example.com", "status": "scheduled", "job_id": "ai-product-designer"},
                    "structured_cv": {
                        "summary": "Product designer focused on enterprise SaaS workflows, research-led design, and cross-functional collaboration.",
                        "skills": ["Figma", "Design Systems", "User Research", "Product Thinking"],
                        "highlights": ["Led enterprise workflow redesigns", "Built reusable design systems", "Improved recruiter and candidate usability"],
                        "source_file": "ava-morgan-portfolio.pdf",
                    },
                    "cv_matching": {"matching_score": 94.8, "passed_threshold": True, "matched_skills": ["Figma", "Design Systems", "User Research"]},
                    "soft_skills": {"overall_score": 91, "communication_score": 92, "leadership_score": 88, "teamwork_score": 91, "adaptability_score": 93},
                    "ego_text": {"ego_level": "low", "ego_score": 18, "reasoning": "Language shows collaborative ownership and shared success."},
                    "final_score": {"composite_score": 90.2, "recommendation": "strong_yes"},
                    "agent_status": {"screening": "completed", "soft_skills": "completed", "ego": "completed", "scheduling": "completed", "interview": "ready", "video_analysis": "pending", "answer_evaluation": "pending"},
                }
            ),
        ),
    )
    notifications = [
        (1, "Interview invitation", "Your AI interview is ready to complete from the portal.", "Interview"),
        (1, "Status update", "Your application has moved into interview scheduling.", "Status"),
        (1, "Selection notice", "You have been shortlisted for the next round.", "Selection"),
    ]
    for candidate_id, title, body, tag in notifications:
        connection.execute("INSERT INTO notifications (candidate_id, title, body, tag) VALUES (?, ?, ?, ?)", (candidate_id, title, body, tag))
    interviews = [
        (1, "AI Interview", "2026-03-27 09:30", "Online", "Confirmed"),
        (1, "Hiring Panel", "2026-03-30 11:00", "Video call", "Pending"),
    ]
    for candidate_id, item_type, date, mode, status in interviews:
        connection.execute("INSERT INTO interviews (candidate_id, type, date, mode, status) VALUES (?, ?, ?, ?, ?)", (candidate_id, item_type, date, mode, status))
    connection.execute(
        "INSERT INTO interview_sessions (candidate_id, session_json) VALUES (?, ?)",
        (
            1,
            _serialize(
                {
                    "session_id": "session-1", "candidate_id": 1, "job_id": "ai-product-designer", "status": "ready", "current_question": 1,
                    "questions": [
                        {"order": 1, "text": "How do you turn complex recruiter requirements into a simple workflow?", "question_type": "behavioral", "expected_answer": "Describe discovery, prioritization, prototyping, and validation with stakeholders.", "guidance": "Mention research, iteration, and measurable outcome."},
                        {"order": 2, "text": "What signals would you surface in an AI hiring dashboard to build trust?", "question_type": "situational", "expected_answer": "Explain transparent scoring, confidence, evidence links, and human override points.", "guidance": "Focus on clarity, bias awareness, and reviewer confidence."},
                        {"order": 3, "text": "Describe a design system decision that improved speed without reducing quality.", "question_type": "technical", "expected_answer": "Give a specific system decision, adoption plan, and impact on quality and delivery speed.", "guidance": "Use a concrete example with impact."},
                    ],
                    "answers": [], "evaluation": None, "fraud_analysis": None,
                }
            ),
        ),
    )
    communications = [
        (
            1,
            "email",
            "outbound",
            "Interview invitation",
            "Your AI interview is ready in the portal.",
            "simulated",
            "local-fallback",
            _serialize({"recipient": "ava@example.com", "template": "status_update"}),
        ),
        (
            1,
            "system",
            "outbound",
            "Shortlist update",
            "Candidate has been shortlisted for the next stage.",
            "recorded",
            "local-system",
            _serialize({"recipient": "ava@example.com", "template": "selection"}),
        ),
    ]
    connection.executemany(
        """
        INSERT INTO communications (candidate_id, channel, direction, subject, body, status, provider, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        communications,
    )
    connection.commit()


def _seed_users(connection: sqlite3.Connection) -> None:
    from backend.services.auth_service import hash_password

    existing = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
    if existing:
        return

    users = [
        ("Admin User", "admin@aihireagent.com", hash_password("Admin@123"), "admin", None),
        ("Hiring Reviewer", "hiring@aihireagent.com", hash_password("Hiring@123"), "hiring", None),
        ("Ava Morgan", "ava@example.com", hash_password("Candidate@123"), "candidate", 1),
    ]
    connection.executemany(
        "INSERT INTO users (full_name, email, password_hash, role, candidate_id, is_active) VALUES (?, ?, ?, ?, ?, 1)",
        users,
    )
    connection.commit()


def init_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                location TEXT,
                type TEXT,
                department TEXT,
                experience TEXT,
                summary TEXT,
                description_json TEXT NOT NULL,
                requirements_json TEXT NOT NULL,
                responsibilities_json TEXT NOT NULL,
                skills_json TEXT NOT NULL,
                salary TEXT,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                label TEXT NOT NULL,
                value TEXT NOT NULL,
                delta TEXT,
                tone TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                role TEXT NOT NULL,
                job_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'received',
                match_score TEXT NOT NULL DEFAULT 'Pending',
                soft_skills TEXT NOT NULL DEFAULT 'Pending',
                ego TEXT NOT NULL DEFAULT 'Pending',
                interview_score TEXT NOT NULL DEFAULT 'Pending',
                fraud_risk TEXT NOT NULL DEFAULT 'Pending',
                timeline_json TEXT NOT NULL,
                linkedin_url TEXT,
                cover_letter TEXT,
                cv_file_path TEXT,
                cv_file_name TEXT,
                cv_file_type TEXT,
                cv_file_size INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS candidate_profiles (
                candidate_id INTEGER PRIMARY KEY,
                profile_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                tag TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                date TEXT NOT NULL,
                mode TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_sessions (
                candidate_id INTEGER PRIMARY KEY,
                session_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                job_id TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS communications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                channel TEXT NOT NULL,
                direction TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                status TEXT NOT NULL,
                provider TEXT,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                candidate_id INTEGER,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _ensure_column(connection, "candidates", "cv_file_path", "TEXT")
        _ensure_column(connection, "candidates", "cv_file_name", "TEXT")
        _ensure_column(connection, "candidates", "cv_file_type", "TEXT")
        _ensure_column(connection, "candidates", "cv_file_size", "INTEGER DEFAULT 0")
        connection.commit()
        _seed_jobs(connection)
        _seed_users(connection)
