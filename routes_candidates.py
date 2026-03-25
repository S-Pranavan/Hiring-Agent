"""
api/routes/candidates.py - Candidate Submission & Pipeline Endpoints
"""

import uuid
import boto3
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.database import get_db
from core.config import settings
from pipeline.cv_pipeline import run_cv_pipeline

router = APIRouter()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def upload_cv_to_s3(file_bytes: bytes, filename: str) -> str:
    key = f"cvs/{uuid.uuid4().hex}/{filename}"
    s3_client.put_object(
        Bucket=settings.S3_BUCKET_CVS,
        Key=key,
        Body=file_bytes,
    )
    return f"https://{settings.S3_BUCKET_CVS}.s3.amazonaws.com/{key}"


# ─── Schemas ──────────────────────────────────────────────────────────────────

class CandidateBasic(BaseModel):
    id: int
    full_name: str
    email: str
    status: str
    job_id: Optional[int]


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_cv(
    background_tasks: BackgroundTasks,
    job_id: int = Form(...),
    full_name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    cv_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Direct web portal CV upload."""
    allowed = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if cv_file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files accepted")

    file_bytes = await cv_file.read()
    s3_url = upload_cv_to_s3(file_bytes, cv_file.filename)
    fmt = "pdf" if cv_file.content_type == "application/pdf" else "docx"

    # Create candidate record
    from sqlalchemy import text
    result = await db.execute(
        text("""
            INSERT INTO candidates (full_name, email, phone, job_id, submission_type, raw_cv_url, cv_format)
            VALUES (:full_name, :email, :phone, :job_id, 'portal', :raw_cv_url, :cv_format)
            RETURNING id
        """),
        {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "job_id": job_id,
            "raw_cv_url": s3_url,
            "cv_format": fmt,
        },
    )
    await db.commit()
    candidate_id = result.scalar_one()

    # Kick off pipeline asynchronously
    background_tasks.add_task(run_cv_pipeline, candidate_id, job_id, s3_url, fmt)

    return {
        "message": "CV received. Processing started.",
        "candidate_id": candidate_id,
    }


@router.get("/")
async def list_candidates(
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List candidates, optionally filtered by job or status."""
    from sqlalchemy import text
    query = "SELECT id, full_name, email, status, job_id FROM candidates WHERE 1=1"
    params = {}
    if job_id:
        query += " AND job_id = :job_id"
        params["job_id"] = job_id
    if status:
        query += " AND status = :status"
        params["status"] = status
    query += " ORDER BY created_at DESC"
    result = await db.execute(text(query), params)
    return [dict(r) for r in result.mappings().all()]


@router.get("/{candidate_id}/profile")
async def get_candidate_profile(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get full candidate profile including all AI scores."""
    from sqlalchemy import text

    candidate = await db.execute(
        text("SELECT * FROM candidates WHERE id = :id"), {"id": candidate_id}
    )
    c = candidate.mappings().one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Fetch associated scores
    matching = await db.execute(
        text("SELECT * FROM cv_matching_results WHERE candidate_id = :id ORDER BY evaluated_at DESC LIMIT 1"),
        {"id": candidate_id},
    )
    soft = await db.execute(
        text("SELECT * FROM soft_skills_analysis WHERE candidate_id = :id LIMIT 1"),
        {"id": candidate_id},
    )
    ego_text = await db.execute(
        text("SELECT * FROM ego_text_analysis WHERE candidate_id = :id LIMIT 1"),
        {"id": candidate_id},
    )
    final = await db.execute(
        text("SELECT * FROM final_scores WHERE candidate_id = :id LIMIT 1"),
        {"id": candidate_id},
    )

    return {
        "candidate": dict(c),
        "cv_matching": dict(matching.mappings().one()) if matching.rowcount else None,
        "soft_skills": dict(soft.mappings().one()) if soft.rowcount else None,
        "ego_text": dict(ego_text.mappings().one()) if ego_text.rowcount else None,
        "final_score": dict(final.mappings().one()) if final.rowcount else None,
    }
