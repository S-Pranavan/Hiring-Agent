from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.auth_service import authenticate_user, issue_access_token, register_candidate_user

router = APIRouter()


class LoginPayload(BaseModel):
    email: str
    password: str
    role: str


class RegisterPayload(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    password: str
    summary: str | None = None


@router.post('/login')
def login(payload: LoginPayload):
    user = authenticate_user(payload.email, payload.password, payload.role)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return {'user': user, 'access_token': issue_access_token(user)}


@router.post('/register', status_code=201)
def register(payload: RegisterPayload):
    full_name = f"{payload.first_name.strip()} {payload.last_name.strip()}".strip()
    try:
        user = register_candidate_user(full_name, payload.email, payload.password, payload.phone, payload.summary)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {'user': user, 'access_token': issue_access_token(user)}
