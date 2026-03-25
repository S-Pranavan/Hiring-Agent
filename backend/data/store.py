from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Store:
    jobs: list[dict[str, Any]]
    metrics: dict[str, list[dict[str, str]]]
    applications: list[dict[str, Any]]
    candidate_profiles: dict[int, dict[str, Any]]
    notifications: dict[int, list[dict[str, str]]]
    interviews: dict[int, list[dict[str, str]]]
    decisions: list[dict[str, Any]]


seed_jobs = [
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
            "Translate complex scoring into confident decision experiences."
        ],
        "requirements": ["Portfolio with SaaS workflow design", "Design systems experience", "Research depth"],
        "responsibilities": [
            "Own candidate and reviewer journeys",
            "Partner with engineering and ML stakeholders",
            "Ship polished enterprise interfaces"
        ],
        "skills": ["Figma", "Design Systems", "User Research", "Product Thinking"],
        "salary": "$60k - $85k",
        "status": "Active"
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
            "Maintain recruiter trust with transparent QA and exception handling."
        ],
        "requirements": ["Hiring operations leadership", "AI tooling familiarity", "Excellent analytics communication"],
        "responsibilities": ["Monitor workflows", "Review fraud signals", "Align decisions with hiring teams"],
        "skills": ["Analytics", "Recruiting Ops", "Stakeholder Management", "Process Design"],
        "salary": "$70k - $95k",
        "status": "Active"
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
            "Implement role-aware analytics, interview tooling, and decision workflows."
        ],
        "requirements": ["Strong React and TypeScript", "API design", "Performance mindset"],
        "responsibilities": ["Build portal features", "Own APIs", "Collaborate with design and data teams"],
        "skills": ["Next.js", "TypeScript", "Node.js", "UX Engineering"],
        "salary": "$90k - $130k",
        "status": "Active"
    }
]

seed_metrics = {
    "candidate": [
        {"label": "Applications", "value": "12", "delta": "3 active", "tone": "brand"},
        {"label": "Interview invites", "value": "2", "delta": "1 this week", "tone": "success"},
        {"label": "Profile strength", "value": "89%", "delta": "Strong", "tone": "brand"},
        {"label": "Response time", "value": "< 24h", "delta": "Average", "tone": "success"}
    ],
    "admin": [
        {"label": "Open roles", "value": "26", "delta": "+4 this week", "tone": "brand"},
        {"label": "Applicants", "value": "1842", "delta": "+18%", "tone": "success"},
        {"label": "Fraud alerts", "value": "17", "delta": "Needs review", "tone": "warn"},
        {"label": "Offer ready", "value": "14", "delta": "High priority", "tone": "brand"}
    ],
    "hiring": [
        {"label": "Assigned roles", "value": "7", "delta": "2 urgent", "tone": "brand"},
        {"label": "Reviews pending", "value": "23", "delta": "Due today", "tone": "warn"},
        {"label": "Strong fit", "value": "11", "delta": "Top quartile", "tone": "success"},
        {"label": "Consensus ready", "value": "6", "delta": "Awaiting signoff", "tone": "brand"}
    ]
}

seed_applications = [
    {
        "id": 1,
        "candidate": "Ava Morgan",
        "email": "ava@example.com",
        "phone": "+94 77 123 4567",
        "role": "AI Product Designer",
        "job_id": "ai-product-designer",
        "status": "Hiring review",
        "match_score": "95%",
        "soft_skills": "91%",
        "ego": "Low",
        "interview_score": "90%",
        "fraud_risk": "Low",
        "timeline": [
            {"stage": "Application submitted", "status": "Completed", "date": "Mar 21", "detail": "CV and portfolio received successfully."},
            {"stage": "AI screening", "status": "Completed", "date": "Mar 22", "detail": "Strong role fit, collaboration, and clarity signals."},
            {"stage": "Hiring review", "status": "In progress", "date": "Mar 24", "detail": "The hiring team is reviewing interview readiness."},
            {"stage": "Interview scheduling", "status": "Upcoming", "date": "Mar 27", "detail": "Slots will be shared once review completes."}
        ]
    }
]

seed_candidate_profiles = {
    1: {
        "candidate": {
            "id": 1,
            "full_name": "Ava Morgan",
            "email": "ava@example.com",
            "status": "shortlisted",
            "job_id": "ai-product-designer"
        },
        "cv_matching": {"matching_score": 94.8, "passed_threshold": True},
        "soft_skills": {"overall_score": 91, "communication_score": 92, "leadership_score": 88},
        "ego_text": {"ego_level": "low", "ego_score": 18},
        "final_score": {"composite_score": 90.2, "recommendation": "strong_yes"}
    }
}

seed_notifications = {
    1: [
        {"title": "Interview invitation", "body": "Senior Product Manager role interview scheduled for Mar 28 at 10:00 AM.", "tag": "Interview"},
        {"title": "Status update", "body": "Your application has moved into hiring review.", "tag": "Status"},
        {"title": "Selection notice", "body": "You have been shortlisted for a final discussion.", "tag": "Selection"}
    ]
}

seed_interviews = {
    1: [
        {"type": "AI Interview", "date": "2026-03-27 09:30", "mode": "Online", "status": "Confirmed"},
        {"type": "Hiring Panel", "date": "2026-03-30 11:00", "mode": "Video call", "status": "Pending"}
    ]
}

store = Store(
    jobs=deepcopy(seed_jobs),
    metrics=deepcopy(seed_metrics),
    applications=deepcopy(seed_applications),
    candidate_profiles=deepcopy(seed_candidate_profiles),
    notifications=deepcopy(seed_notifications),
    interviews=deepcopy(seed_interviews),
    decisions=[]
)


def list_jobs() -> list[dict[str, Any]]:
    return deepcopy(store.jobs)


def get_job(job_id: str) -> dict[str, Any] | None:
    return deepcopy(next((job for job in store.jobs if job["id"] == job_id), None))


def list_metrics(role: str) -> list[dict[str, str]]:
    return deepcopy(store.metrics.get(role, store.metrics["candidate"]))


def list_applications() -> list[dict[str, Any]]:
    return deepcopy(store.applications)


def get_application(application_id: int) -> dict[str, Any] | None:
    return deepcopy(next((application for application in store.applications if application["id"] == application_id), None))


def create_application(payload: dict[str, Any]) -> dict[str, Any]:
    application_id = len(store.applications) + 1
    application = {
        "id": application_id,
        "candidate": payload["full_name"],
        "email": payload["email"],
        "phone": payload.get("phone", ""),
        "role": payload["role"],
        "job_id": payload["job_id"],
        "status": "received",
        "match_score": "Pending",
        "soft_skills": "Pending",
        "ego": "Pending",
        "interview_score": "Pending",
        "fraud_risk": "Pending",
        "timeline": [
            {
                "stage": "Application submitted",
                "status": "Completed",
                "date": datetime.utcnow().strftime("%b %d"),
                "detail": "Application received through the portal."
            },
            {
                "stage": "AI screening",
                "status": "Upcoming",
                "date": "Pending",
                "detail": "The backend queue will evaluate the application next."
            }
        ]
    }
    store.applications.append(application)
    store.candidate_profiles[application_id] = {
        "candidate": {
            "id": application_id,
            "full_name": payload["full_name"],
            "email": payload["email"],
            "status": "received",
            "job_id": payload["job_id"]
        },
        "cv_matching": None,
        "soft_skills": None,
        "ego_text": None,
        "final_score": None
    }
    store.notifications[application_id] = [
        {
            "title": "Application received",
            "body": f"Your application for {payload['role']} was submitted successfully.",
            "tag": "Application"
        }
    ]
    store.interviews[application_id] = []
    return deepcopy(application)


def get_candidate_profile(candidate_id: int) -> dict[str, Any] | None:
    return deepcopy(store.candidate_profiles.get(candidate_id))


def get_dashboard_summary() -> dict[str, int]:
    return {
        "received": len(store.applications),
        "shortlisted": 4,
        "interviewed": 3,
        "selected": 1,
        "fraud_alerts": 1
    }


def get_notifications(candidate_id: int) -> list[dict[str, str]]:
    return deepcopy(store.notifications.get(candidate_id, []))


def get_interviews(candidate_id: int) -> list[dict[str, str]]:
    return deepcopy(store.interviews.get(candidate_id, []))


def record_decision(payload: dict[str, Any], decision_type: str) -> dict[str, Any]:
    decision = {"decision_type": decision_type, **payload}
    store.decisions.append(decision)
    return deepcopy(decision)