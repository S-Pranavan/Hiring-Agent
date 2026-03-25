"""
api/routes/jobs.py - Job Management Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from core.database import get_db

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: str = "full-time"


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    department: Optional[str]
    location: Optional[str]
    employment_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)):
    """Create a new job opening."""
    from sqlalchemy import text
    result = await db.execute(
        text("""
            INSERT INTO jobs (title, description, requirements, department, location, employment_type)
            VALUES (:title, :description, :requirements, :department, :location, :employment_type)
            RETURNING *
        """),
        payload.model_dump(),
    )
    await db.commit()
    row = result.mappings().one()
    return dict(row)


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all jobs, optionally filtered by status."""
    from sqlalchemy import text
    query = "SELECT * FROM jobs"
    params = {}
    if status:
        query += " WHERE status = :status"
        params["status"] = status
    query += " ORDER BY created_at DESC"
    result = await db.execute(text(query), params)
    return [dict(r) for r in result.mappings().all()]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single job by ID."""
    from sqlalchemy import text
    result = await db.execute(text("SELECT * FROM jobs WHERE id = :id"), {"id": job_id})
    row = result.mappings().one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(row)


@router.patch("/{job_id}/status")
async def update_job_status(
    job_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db),
):
    """Open, close, or pause a job."""
    if new_status not in ("open", "closed", "paused"):
        raise HTTPException(status_code=400, detail="Invalid status")
    from sqlalchemy import text
    await db.execute(
        text("UPDATE jobs SET status = :status WHERE id = :id"),
        {"status": new_status, "id": job_id},
    )
    await db.commit()
    return {"message": f"Job {job_id} status updated to {new_status}"}
