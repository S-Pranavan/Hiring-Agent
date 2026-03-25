from fastapi import APIRouter

from backend.data.store import get_interviews, get_notifications

router = APIRouter()


@router.get("/candidate/{candidate_id}")
def read_candidate_interviews(candidate_id: int):
    return {"items": get_interviews(candidate_id)}


@router.get("/candidate/{candidate_id}/notifications")
def read_candidate_notifications(candidate_id: int):
    return {"items": get_notifications(candidate_id)}