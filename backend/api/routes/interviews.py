from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.api.deps import ensure_candidate_access, require_roles
from backend.data.store import get_interview_session, get_interviews, get_notifications
from backend.services.agent_orchestrator import attach_interview_evidence, submit_answer

router = APIRouter()
ALLOWED_VIDEO_SUFFIXES = {".webm", ".mp4", ".mov"}
MAX_VIDEO_BYTES = 100 * 1024 * 1024


class AnswerPayload(BaseModel):
    question_order: int
    answer_text: str
    answer_type: str = "text"


@router.get("/candidate/{candidate_id}")
def read_candidate_interviews(candidate_id: int, user=Depends(require_roles("candidate", "admin", "hiring"))):
    ensure_candidate_access(candidate_id, user)
    return {"items": get_interviews(candidate_id)}


@router.get("/candidate/{candidate_id}/notifications")
def read_candidate_notifications(candidate_id: int, user=Depends(require_roles("candidate", "admin", "hiring"))):
    ensure_candidate_access(candidate_id, user)
    return {"items": get_notifications(candidate_id)}


@router.get("/candidate/{candidate_id}/session")
def read_candidate_session(candidate_id: int, user=Depends(require_roles("candidate", "admin", "hiring"))):
    ensure_candidate_access(candidate_id, user)
    session = get_interview_session(candidate_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return {"session": session}


@router.post("/candidate/{candidate_id}/answers")
def submit_candidate_answer(candidate_id: int, payload: AnswerPayload, user=Depends(require_roles("candidate", "admin", "hiring"))):
    ensure_candidate_access(candidate_id, user)
    try:
        session = submit_answer(candidate_id, payload.question_order, payload.answer_text, payload.answer_type)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"session": session}


@router.post("/candidate/{candidate_id}/complete")
async def upload_candidate_evidence(
    candidate_id: int,
    video_file: UploadFile | None = File(None),
    notes: str | None = Form(default=""),
    user=Depends(require_roles("candidate", "admin", "hiring")),
):
    ensure_candidate_access(candidate_id, user)
    if video_file is None or not video_file.filename:
        raise HTTPException(status_code=400, detail="Interview recording is required")

    suffix = Path(video_file.filename).suffix.lower()
    if suffix not in ALLOWED_VIDEO_SUFFIXES:
        raise HTTPException(status_code=400, detail="Only WEBM, MP4, and MOV recordings are supported")

    file_bytes = await video_file.read()
    if len(file_bytes) > MAX_VIDEO_BYTES:
        raise HTTPException(status_code=400, detail="Interview recording exceeds 100MB limit")

    try:
        session = attach_interview_evidence(candidate_id, video_file.filename, video_file.content_type or "application/octet-stream", file_bytes, notes or "")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"session": session, "uploaded_at": datetime.utcnow().isoformat()}
