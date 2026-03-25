from fastapi import APIRouter
from pydantic import BaseModel

from backend.data.store import record_decision

router = APIRouter()


class DecisionPayload(BaseModel):
    candidate_id: int
    job_id: str
    notes: str | None = None
    joining_date: str | None = None
    interview_date: str | None = None
    interview_time: str | None = None
    location: str | None = None


@router.post("/decide/direct-hire")
def direct_hire(payload: DecisionPayload):
    return {"message": "Direct hire recorded", "decision": record_decision(payload.model_dump(), "direct_hire")}


@router.post("/decide/physical-interview")
def physical_interview(payload: DecisionPayload):
    return {"message": "Physical interview recorded", "decision": record_decision(payload.model_dump(), "physical_interview")}


@router.post("/decide/reject")
def reject(payload: DecisionPayload):
    return {"message": "Rejection recorded", "decision": record_decision(payload.model_dump(), "reject")}