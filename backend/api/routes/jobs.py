from fastapi import APIRouter, HTTPException

from backend.data.store import get_job, list_jobs

router = APIRouter()


@router.get("/")
def read_jobs():
    return {"jobs": list_jobs()}


@router.get("/{job_id}")
def read_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job": job}