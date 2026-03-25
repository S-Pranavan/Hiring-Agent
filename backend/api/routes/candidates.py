from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.data.store import create_application, get_candidate_profile, list_applications

router = APIRouter()


class ApplicationPayload(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    role: str
    job_id: str
    linkedin_url: str | None = None
    cover_letter: str | None = None


@router.get("/")
def read_candidates():
    return {"applications": list_applications()}


@router.get("/{candidate_id}/profile")
def read_candidate_profile(candidate_id: int):
    profile = get_candidate_profile(candidate_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return profile


@router.post("/upload", status_code=201)
def upload_candidate_application(payload: ApplicationPayload):
    application = create_application(payload.model_dump())
    return {
        "message": "Application received. Processing started.",
        "candidate_id": application["id"],
        "application": application
    }