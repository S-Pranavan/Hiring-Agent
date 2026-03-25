from fastapi import APIRouter

from backend.data.store import get_dashboard_summary, list_metrics

router = APIRouter()


@router.get("/metrics")
def read_metrics(role: str = "candidate"):
    return {"role": role, "metrics": list_metrics(role)}


@router.get("/summary")
def read_summary():
    return get_dashboard_summary()