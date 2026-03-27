from fastapi import Depends, Header, HTTPException, status

from backend.services.auth_service import verify_access_token


def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    token = authorization.split(" ", 1)[1]
    user = verify_access_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


def require_roles(*roles: str):
    def _dependency(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _dependency


def ensure_candidate_access(candidate_id: int, user: dict):
    if user["role"] == "candidate" and user.get("candidate_id") != candidate_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access another candidate record")
