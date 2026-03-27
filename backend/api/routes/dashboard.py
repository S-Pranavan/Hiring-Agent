from fastapi import APIRouter, Depends

from backend.api.deps import require_roles
from backend.data.store import get_dashboard_summary, list_metrics

router = APIRouter()


@router.get("/metrics")
def read_metrics(role: str = "candidate", user=Depends(require_roles("candidate", "admin", "hiring"))):
    if user["role"] == "candidate":
        role = "candidate"
    return {"role": role, "metrics": list_metrics(role)}


@router.get("/summary")
def read_summary(user=Depends(require_roles("admin", "hiring"))):
    return get_dashboard_summary()
