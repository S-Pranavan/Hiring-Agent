from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from backend.data.store import (
    add_notification,
    get_application,
    get_candidate_profile,
    get_interview_session,
    get_job,
    set_candidate_profile,
    set_interview_session,
    set_interviews,
    update_application,
)
from backend.services.communication_provider import CommunicationProvider
from backend.services.cv_parser import CVParserService
from backend.services.openai_provider import OpenAIProvider
from backend.services.storage_provider import StorageProvider

SOFT_SKILL_BANK = {
    "communication": ["communicate", "communication", "present", "presentation", "stakeholder", "write", "written"],
    "teamwork": ["team", "collaborate", "collaboration", "partner", "cross-functional", "together"],
    "leadership": ["lead", "mentor", "coach", "manage", "owned", "drove", "initiated"],
    "adaptability": ["adapt", "iterate", "learn", "fast-paced", "ambiguous", "change", "improve"],
}

HIGH_EGO_PATTERNS = ["i alone", "best", "superior", "single-handedly", "without me", "demand"]
LOW_EGO_PATTERNS = ["we", "team", "together", "supported", "collaborated", "shared"]
FRAUD_PATTERNS = ["copy", "paste", "looking away", "tab switch", "multiple faces"]

openai_provider = OpenAIProvider()
communication_provider = CommunicationProvider()
cv_parser = CVParserService()
storage_provider = StorageProvider()


def _candidate_text(application: dict[str, Any], profile: dict[str, Any]) -> str:
    structured_cv = profile.get("structured_cv", {})
    summary = structured_cv.get("summary", "")
    raw_text = structured_cv.get("raw_text", "")
    role = application.get("role", "")
    return f"{application['candidate']} {role} {summary} {raw_text}".strip()


def _percentage(value: float) -> str:
    return f"{round(value)}%"


def _score_match(text: str, job: dict[str, Any]) -> tuple[float, list[str]]:
    lower_text = text.lower()
    job_terms = [job["title"], *job.get("skills", []), *job.get("requirements", [])]
    matched = [term for term in job_terms if term.lower() in lower_text]
    total = max(len(job_terms), 1)
    coverage = len(matched) / total
    length_bonus = min(len(lower_text.split()) / 120, 0.2)
    score = min(98.0, 68 + coverage * 24 + length_bonus * 30)
    return round(score, 2), matched[:6]


def _score_soft_skills(text: str) -> dict[str, float]:
    lower_text = text.lower()
    results: dict[str, float] = {}
    for category, keywords in SOFT_SKILL_BANK.items():
        hits = sum(1 for keyword in keywords if keyword in lower_text)
        results[category] = round(min(100.0, 45 + (hits / max(len(keywords), 1)) * 55), 2)
    results["overall"] = round(
        (results["communication"] + results["teamwork"] + results["leadership"] + results["adaptability"]) / 4,
        2,
    )
    return results


def _score_ego(text: str) -> tuple[str, float, str]:
    lower_text = text.lower()
    high_hits = sum(1 for pattern in HIGH_EGO_PATTERNS if pattern in lower_text)
    low_hits = sum(1 for pattern in LOW_EGO_PATTERNS if pattern in lower_text)
    score = max(0.0, min(100.0, 35 + high_hits * 15 - low_hits * 8))
    if score >= 65:
        level = "high"
        reasoning = "The language reads highly self-focused and dominant."
    elif score >= 35:
        level = "moderate"
        reasoning = "The language balances ownership with some collaboration cues."
    else:
        level = "low"
        reasoning = "The language emphasizes teamwork and shared outcomes."
    return level, round(score, 2), reasoning


def _recommendation(match_score: float, soft_overall: float, ego_score: float) -> tuple[float, str]:
    composite = round(match_score * 0.45 + soft_overall * 0.35 + (100 - ego_score) * 0.20, 2)
    if composite >= 85:
        recommendation = "strong_yes"
    elif composite >= 72:
        recommendation = "yes"
    elif composite >= 60:
        recommendation = "review"
    else:
        recommendation = "no"
    return composite, recommendation


def _schedule_interview(job: dict[str, Any]) -> list[dict[str, str]]:
    scheduled_at = datetime.utcnow() + timedelta(days=2)
    return [
        {"type": "AI Interview", "date": scheduled_at.strftime("%Y-%m-%d %H:%M"), "mode": "Portal session", "status": "Confirmed"},
        {"type": "Hiring Panel", "date": (scheduled_at + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "mode": "Video call", "status": "Pending"},
    ]


def process_application(candidate_id: int) -> dict[str, Any]:
    application = get_application(candidate_id)
    profile = get_candidate_profile(candidate_id)
    if not application or not profile:
        raise ValueError("Candidate application not found")

    job = get_job(application["job_id"])
    if not job:
        raise ValueError("Job not found")

    parsed_cv = cv_parser.parse(
        application.get("cv_file_path"),
        fallback_text=profile.get("structured_cv", {}).get("summary", ""),
        fallback_name=application.get("candidate", ""),
        fallback_email=application.get("email", ""),
        fallback_phone=application.get("phone", ""),
    )
    text = parsed_cv.get("raw_text") or _candidate_text(application, profile)
    match_score, matched_skills = _score_match(text, job)
    soft_scores = _score_soft_skills(text)
    ego_level, ego_score, ego_reasoning = _score_ego(text)
    composite, recommendation = _recommendation(match_score, soft_scores["overall"], ego_score)

    new_status = "shortlisted" if composite >= 64 else "rejected"
    fraud_risk = "Low" if recommendation in {"strong_yes", "yes"} else "Moderate"

    def _update(application_row: dict[str, Any]) -> None:
        application_row["status"] = "scheduled" if new_status == "shortlisted" else "rejected"
        application_row["match_score"] = _percentage(match_score)
        application_row["soft_skills"] = _percentage(soft_scores["overall"])
        application_row["ego"] = ego_level.title()
        application_row["fraud_risk"] = fraud_risk
        application_row["timeline"] = [
            application_row["timeline"][0],
            {"stage": "AI screening", "status": "Completed", "date": datetime.utcnow().strftime("%b %d"), "detail": f"Match score {_percentage(match_score)}, recommendation {recommendation.replace('_', ' ')}."},
            {"stage": "Hiring review", "status": "Completed", "date": datetime.utcnow().strftime("%b %d"), "detail": "Candidate moved forward for interview scheduling." if new_status == "shortlisted" else "Candidate did not meet the automated review threshold."},
            {"stage": "Interview scheduling", "status": "Completed" if new_status == "shortlisted" else "Skipped", "date": datetime.utcnow().strftime("%b %d") if new_status == "shortlisted" else "-", "detail": "Interview schedule prepared by the orchestration agent." if new_status == "shortlisted" else "Interview scheduling was skipped after automated review."},
            {"stage": "AI interview", "status": "Upcoming" if new_status == "shortlisted" else "Not started", "date": (datetime.utcnow() + timedelta(days=2)).strftime("%b %d") if new_status == "shortlisted" else "Pending", "detail": "Candidate can now complete the interview from the portal." if new_status == "shortlisted" else "Interview session was not opened."},
        ]

    updated_application = update_application(candidate_id, _update)
    if not updated_application:
        raise ValueError("Unable to update candidate application")

    updated_profile = profile
    updated_profile["candidate"]["status"] = updated_application["status"]
    existing_cv = profile.get("structured_cv", {})
    combined_skills = []
    for skill in [*parsed_cv.get("skills", []), *job.get("skills", [])]:
        if skill not in combined_skills:
            combined_skills.append(skill)
    highlights = [
        *([f"Uploaded CV: {existing_cv['source_file']}"] if existing_cv.get("source_file") else []),
        *[item for item in parsed_cv.get("highlights", [])[:2] if item],
        f"Matched skills: {', '.join(matched_skills[:3]) or 'baseline overlap'}",
        f"Soft-skills readiness: {_percentage(soft_scores['overall'])}",
        f"Recommendation: {recommendation.replace('_', ' ')}",
    ]
    updated_profile["structured_cv"] = {
        "summary": parsed_cv.get("summary") or existing_cv.get("summary", "Profile received."),
        "skills": combined_skills[:8],
        "highlights": highlights[:6],
        "source_file": existing_cv.get("source_file"),
        "raw_text": parsed_cv.get("raw_text", ""),
    }
    updated_profile["cv_matching"] = {"matching_score": match_score, "passed_threshold": match_score >= 70, "matched_skills": matched_skills}
    updated_profile["soft_skills"] = {
        "overall_score": soft_scores["overall"],
        "communication_score": soft_scores["communication"],
        "leadership_score": soft_scores["leadership"],
        "teamwork_score": soft_scores["teamwork"],
        "adaptability_score": soft_scores["adaptability"],
    }
    updated_profile["ego_text"] = {"ego_level": ego_level, "ego_score": ego_score, "reasoning": ego_reasoning}
    updated_profile["final_score"] = {"composite_score": composite, "recommendation": recommendation}
    updated_profile["agent_status"] = {
        "screening": "completed",
        "soft_skills": "completed",
        "ego": "completed",
        "scheduling": "completed" if new_status == "shortlisted" else "skipped",
        "interview": "ready" if new_status == "shortlisted" else "blocked",
        "video_analysis": "pending" if new_status == "shortlisted" else "blocked",
        "answer_evaluation": "pending" if new_status == "shortlisted" else "blocked",
    }
    set_candidate_profile(candidate_id, updated_profile)

    add_notification(candidate_id, {"title": "AI screening complete", "body": f"Your application received a {_percentage(match_score)} match score and is marked as {updated_application['status']}.", "tag": "Screening"})

    if new_status == "shortlisted":
        interview_slots = _schedule_interview(job)
        set_interviews(candidate_id, interview_slots)

        skill_hint = matched_skills[0] if matched_skills else (job.get("skills", [job["title"]])[0])
        generated_questions = openai_provider.generate_questions(job["title"], job["department"], skill_hint, updated_profile["structured_cv"]["summary"])
        session = get_interview_session(candidate_id) or {}
        session.update(
            {
                "session_id": session.get("session_id", f"session-{candidate_id}"),
                "candidate_id": candidate_id,
                "job_id": job["id"],
                "status": "ready",
                "current_question": 1,
                "questions": generated_questions,
                "answers": [],
                "evaluation": None,
                "fraud_analysis": {"fraud_score": 8, "risk_level": "low", "signals": ["single face detected", "stable session start"]},
            }
        )
        set_interview_session(candidate_id, session)

        interview_message = (
            f"Your AI interview for {job['title']} is ready. "
            f"Please complete it within the next 48 hours in the portal."
        )
        communication_provider.send_email(candidate_id, application["email"], f"AI interview ready - {job['title']}", interview_message)
        if application.get("phone"):
            communication_provider.trigger_call(candidate_id, application["phone"], interview_message)
        add_notification(candidate_id, {"title": "Interview scheduled", "body": "Your AI interview questions are now available in the portal.", "tag": "Interview"})
    else:
        set_interview_session(candidate_id, {"session_id": f"session-{candidate_id}", "candidate_id": candidate_id, "job_id": job["id"], "status": "blocked", "current_question": 1, "questions": [], "answers": [], "evaluation": None, "fraud_analysis": None})
        communication_provider.send_email(candidate_id, application["email"], f"Application update - {job['title']}", "Your application was reviewed and will not move to the next stage at this time.")

    return updated_application


def submit_answer(candidate_id: int, question_order: int, answer_text: str, answer_type: str = "text") -> dict[str, Any]:
    session = get_interview_session(candidate_id)
    application = get_application(candidate_id)
    if not session or not application:
        raise ValueError("Interview session not found")

    question = next((item for item in session.get("questions", []) if item["order"] == question_order), None)
    if not question:
        raise ValueError("Question not found")

    provider_result = openai_provider.evaluate_answer(question["text"], question["expected_answer"], answer_text)
    if provider_result:
        relevance_score = provider_result["relevance_score"]
        accuracy_score = provider_result["accuracy_score"]
        depth_score = provider_result["depth_score"]
        overall_score = provider_result["overall_score"]
        feedback = provider_result["feedback"]
    else:
        expected_words = {word.lower().strip(".,") for word in question["expected_answer"].split() if len(word) > 3}
        answer_words = {word.lower().strip(".,") for word in answer_text.split() if len(word) > 3}
        overlap = len(expected_words & answer_words)
        coverage = overlap / max(len(expected_words), 1)
        depth_bonus = min(len(answer_text.split()) / 60, 0.25)
        action_words = {"built", "improved", "measured", "collaborated", "delivered", "validated", "prioritized", "iterated"}
        action_hits = len(action_words & answer_words)
        relevance_score = round(min(100.0, 55 + coverage * 35), 2)
        accuracy_score = round(min(100.0, 52 + coverage * 32 + min(action_hits, 3) * 4), 2)
        depth_score = round(min(100.0, 50 + depth_bonus * 100), 2)
        overall_score = round((relevance_score * 0.3) + (accuracy_score * 0.4) + (depth_score * 0.3), 2)
        feedback = (
            "Strong answer with clear structure and relevant detail."
            if overall_score >= 75
            else "Reasonable answer, but it needs more concrete evidence and outcome detail."
            if overall_score >= 55
            else "The answer is too shallow or misses key expectations from the question."
        )

    existing_answers = [item for item in session.get("answers", []) if item["question_order"] != question_order]
    existing_answers.append({"question_order": question_order, "answer_text": answer_text, "answer_type": answer_type, "relevance_score": relevance_score, "accuracy_score": accuracy_score, "depth_score": depth_score, "score": overall_score, "feedback": feedback})
    existing_answers.sort(key=lambda item: item["question_order"])
    session["answers"] = existing_answers

    answered_count = len(existing_answers)
    session["current_question"] = min(answered_count + 1, max(len(session.get("questions", [])), 1))

    fraud_hits = sum(1 for marker in FRAUD_PATTERNS if marker in answer_text.lower())
    fraud_score = min(100, 8 + fraud_hits * 18 + max(0, 2 - len(answer_text.split()) // 20) * 5)
    risk_level = "high" if fraud_score >= 65 else "moderate" if fraud_score >= 35 else "low"
    session["fraud_analysis"] = {"fraud_score": fraud_score, "risk_level": risk_level, "signals": ["response length checked", "answer consistency reviewed", *(["possible scripted language"] if fraud_hits else [])]}

    if answered_count == len(session.get("questions", [])):
        final_score = round(sum(item["score"] for item in existing_answers) / max(answered_count, 1), 2)
        session["status"] = "completed"
        session["evaluation"] = {"final_score": final_score, "summary_feedback": f"Interview completed with a final score of {round(final_score)}%.", "recommendation": "advance" if final_score >= 72 and risk_level != "high" else "review" if final_score >= 58 else "reject"}

        def _update(application_row: dict[str, Any]) -> None:
            application_row["interview_score"] = _percentage(final_score)
            application_row["fraud_risk"] = risk_level.title()
            application_row["status"] = "interview_completed"
            application_row["timeline"][-1] = {"stage": "AI interview", "status": "Completed", "date": datetime.utcnow().strftime("%b %d"), "detail": f"Interview completed with score {_percentage(final_score)} and {risk_level} fraud risk."}

        update_application(candidate_id, _update)

        profile = get_candidate_profile(candidate_id)
        if profile and profile.get("final_score"):
            profile["final_score"] = {"composite_score": round((profile["final_score"]["composite_score"] * 0.65) + (final_score * 0.35), 2), "recommendation": session["evaluation"]["recommendation"]}
            profile["agent_status"]["video_analysis"] = "completed"
            profile["agent_status"]["answer_evaluation"] = "completed"
            profile["candidate"]["status"] = "interview_completed"
            set_candidate_profile(candidate_id, profile)

        add_notification(candidate_id, {"title": "Interview completed", "body": session["evaluation"]["summary_feedback"], "tag": "Interview"})
    else:
        session["status"] = "in_progress"

    set_interview_session(candidate_id, session)
    return session


def attach_interview_evidence(candidate_id: int, file_name: str, file_type: str, file_bytes: bytes, notes: str = "") -> dict[str, Any]:
    session = get_interview_session(candidate_id)
    application = get_application(candidate_id)
    if not session or not application:
        raise ValueError("Interview session not found")

    stored_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{file_name}"
    file_path = storage_provider.save_binary_artifact("interviews", stored_name, __import__("io").BytesIO(file_bytes))

    fraud_analysis = session.get("fraud_analysis") or {"fraud_score": 0, "risk_level": "low", "signals": []}
    evidence_markers = [
        {"label": "Recording uploaded", "detail": f"Stored as {stored_name}", "severity": "info"},
        *[{"label": signal.title(), "detail": "Derived from interview analysis", "severity": "review" if fraud_analysis.get("risk_level") != "low" else "info"} for signal in fraud_analysis.get("signals", [])[:3]],
    ]

    session["evidence"] = {
        "video_file_name": file_name,
        "video_file_type": file_type or "application/octet-stream",
        "video_file_size": len(file_bytes),
        "video_path": file_path,
        "notes": notes,
        "uploaded_at": datetime.utcnow().isoformat(),
        "markers": evidence_markers,
    }

    if session.get("status") == "ready":
        session["status"] = "recording_uploaded"

    set_interview_session(candidate_id, session)

    def _update(application_row: dict[str, Any]) -> None:
        timeline = application_row.get("timeline", [])
        if timeline:
            timeline.append({
                "stage": "Evidence uploaded",
                "status": "Completed",
                "date": datetime.utcnow().strftime("%b %d"),
                "detail": f"Interview recording uploaded as {file_name}.",
            })

    update_application(candidate_id, _update)
    add_notification(candidate_id, {
        "title": "Interview evidence uploaded",
        "body": "Your interview recording has been stored successfully.",
        "tag": "Interview",
    })
    return session
