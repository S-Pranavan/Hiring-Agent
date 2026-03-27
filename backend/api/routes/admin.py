from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.deps import require_roles
from backend.data.store import add_notification, get_application, list_communications, record_decision
from backend.services.communication_provider import CommunicationProvider

router = APIRouter()
communication_provider = CommunicationProvider()


class DecisionPayload(BaseModel):
    candidate_id: int
    job_id: str
    notes: str | None = None
    joining_date: str | None = None
    interview_date: str | None = None
    interview_time: str | None = None
    location: str | None = None


class CommunicationPayload(BaseModel):
    candidate_id: int
    template: str
    channel: str = "email"
    custom_message: str | None = None


def _build_template(template: str, candidate_name: str, role_title: str) -> tuple[str, str]:
    templates: dict[str, tuple[str, str]] = {
        "rejection": (
            f"Update on your {role_title} application",
            f"Hello {candidate_name},\n\nThank you for your interest in the {role_title} role. After review, we will not be moving forward at this stage.\n\nWe appreciate the time you invested and encourage you to apply again in the future.\n",
        ),
        "selection": (
            f"Next steps for the {role_title} role",
            f"Hello {candidate_name},\n\nWe are pleased to share that you have been selected to move forward for the {role_title} role.\n\nOur team will follow up with final onboarding details shortly.\n",
        ),
        "physical_interview": (
            f"Physical interview invitation for {role_title}",
            f"Hello {candidate_name},\n\nYou have been invited to a physical interview for the {role_title} role. Please review the portal for scheduling details and confirm your availability.\n",
        ),
        "status_update": (
            f"Status update for your {role_title} application",
            f"Hello {candidate_name},\n\nYour application for the {role_title} role has been updated in our hiring workflow. Please sign in to the portal to review the latest status.\n",
        ),
    }
    return templates.get(template, templates["status_update"])


@router.get("/communications")
def read_communications(user=Depends(require_roles("admin", "hiring"))):
    return {"items": list_communications()}


@router.post("/communications/send")
def send_communication(payload: CommunicationPayload, user=Depends(require_roles("admin", "hiring"))):
    application = get_application(payload.candidate_id)
    if not application:
        raise HTTPException(status_code=404, detail="Candidate not found")

    subject, message = _build_template(payload.template, application["candidate"], application["role"])
    if payload.custom_message and payload.custom_message.strip():
        message = payload.custom_message.strip()

    if payload.channel == "call":
        if not application.get("phone"):
            raise HTTPException(status_code=400, detail="Candidate phone number is not available")
        result = communication_provider.trigger_call(payload.candidate_id, application["phone"], message)
    else:
        result = communication_provider.send_email(payload.candidate_id, application["email"], subject, message)

    add_notification(
        payload.candidate_id,
        {
            "title": "Communication sent",
            "body": f"{payload.template.replace('_', ' ').title()} sent via {payload.channel}.",
            "tag": "Communication",
        },
    )

    return {
        "message": "Communication processed.",
        "delivery": result,
        "candidate_id": payload.candidate_id,
    }


@router.post("/decide/direct-hire")
def direct_hire(payload: DecisionPayload, user=Depends(require_roles("admin"))):
    return {"message": "Direct hire recorded", "decision": record_decision(payload.model_dump(), "direct_hire")}


@router.post("/decide/physical-interview")
def physical_interview(payload: DecisionPayload, user=Depends(require_roles("admin"))):
    return {"message": "Physical interview recorded", "decision": record_decision(payload.model_dump(), "physical_interview")}


@router.post("/decide/reject")
def reject(payload: DecisionPayload, user=Depends(require_roles("admin", "hiring"))):
    return {"message": "Rejection recorded", "decision": record_decision(payload.model_dump(), "reject")}


@router.post("/decide/shortlist")
def shortlist(payload: DecisionPayload, user=Depends(require_roles("admin", "hiring"))):
    return {"message": "Shortlist recorded", "decision": record_decision(payload.model_dump(), "shortlist")}


@router.post("/decide/select")
def select(payload: DecisionPayload, user=Depends(require_roles("admin", "hiring"))):
    return {"message": "Selection recorded", "decision": record_decision(payload.model_dump(), "select")}
