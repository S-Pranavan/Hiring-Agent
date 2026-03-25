"""
AI Hiring Agent System - FastAPI Backend
main.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import jobs, candidates, interviews, admin, webhooks
from core.config import settings
from core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="AI Hiring Agent System",
    description="Automated recruitment pipeline powered by multi-agent AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(jobs.router,        prefix="/api/v1/jobs",        tags=["Jobs"])
app.include_router(candidates.router,  prefix="/api/v1/candidates",  tags=["Candidates"])
app.include_router(interviews.router,  prefix="/api/v1/interviews",  tags=["Interviews"])
app.include_router(admin.router,       prefix="/api/v1/admin",       tags=["Admin"])
app.include_router(webhooks.router,    prefix="/api/v1/webhooks",    tags=["Webhooks"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
