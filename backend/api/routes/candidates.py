from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.api.deps import ensure_candidate_access, require_roles
from backend.data.store import create_application, get_candidate_profile, get_user_applications, list_applications
from backend.services.agent_orchestrator import process_application
from backend.services.storage_provider import StorageProvider

router = APIRouter()
storage_provider = StorageProvider()
ALLOWED_SUFFIXES = {".pdf", ".doc", ".docx"}
MAX_FILE_BYTES = 10 * 1024 * 1024


@router.get("/")
def read_candidates(user=Depends(require_roles("candidate", "admin", "hiring"))):
    if user["role"] == "candidate":
        return {"applications": get_user_applications(user["candidate_id"]) }
    return {"applications": list_applications()}


@router.get("/{candidate_id}/profile")
def read_candidate_profile(candidate_id: int, user=Depends(require_roles("candidate", "admin", "hiring"))):
    ensure_candidate_access(candidate_id, user)
    profile = get_candidate_profile(candidate_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return profile


@router.post("/upload", status_code=201)
async def upload_candidate_application(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str | None = Form(None),
    role: str = Form(...),
    job_id: str = Form(...),
    linkedin_url: str | None = Form(None),
    cover_letter: str | None = Form(None),
    cv_file: UploadFile | None = File(None),
):
    file_path = ""
    file_name = ""
    file_type = ""
    file_size = 0

    if cv_file is not None and cv_file.filename:
        suffix = Path(cv_file.filename).suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are supported")

        file_bytes = await cv_file.read()
        file_size = len(file_bytes)
        if file_size > MAX_FILE_BYTES:
            raise HTTPException(status_code=400, detail="CV file exceeds 10MB limit")

        file_name = cv_file.filename
        file_type = cv_file.content_type or "application/octet-stream"
        stored_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{file_name}"
        file_path = storage_provider.save_binary_artifact("cvs", stored_name, __import__("io").BytesIO(file_bytes))

    application = create_application(
        {
            "full_name": full_name,
            "email": email,
            "phone": phone or "",
            "role": role,
            "job_id": job_id,
            "linkedin_url": linkedin_url or "",
            "cover_letter": cover_letter or "",
            "cv_file_path": file_path,
            "cv_file_name": file_name,
            "cv_file_type": file_type,
            "cv_file_size": file_size,
        }
    )
    processed_application = process_application(application["id"])
    return {
        "message": "Application received and processed.",
        "candidate_id": application["id"],
        "application": processed_application,
    }
