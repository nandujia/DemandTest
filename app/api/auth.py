from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.deps import get_current_user
from app.auth.tokens import create_access_token
from app.models.user import LoginRequest, LoginResponse, RegisterRequest, UserPublic, UserRecord
from app.services.user_service import user_service


router = APIRouter()


@router.post("/auth/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="两次密码不一致")
    user = user_service.create_user(
        phone=request.phone,
        username=request.username,
        password=request.password,
    )
    token = create_access_token(user_id=user.id, username=user.username)
    return LoginResponse(token=token, user=user)


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = user_service.authenticate(identifier=request.identifier, password=request.password)
    token = create_access_token(user_id=user.id, username=user.username)
    return LoginResponse(token=token, user=user)


@router.get("/auth/me", response_model=UserPublic)
async def me(current_user: UserRecord = Depends(get_current_user)):
    return UserPublic(
        id=current_user.id,
        phone=current_user.phone,
        username=current_user.username,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
    )
