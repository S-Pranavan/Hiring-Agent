from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import admin, candidates, dashboard, interviews, jobs
from backend.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["candidates"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(interviews.router, prefix="/api/v1/interviews", tags=["interviews"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.app_version}