from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserRecord(BaseModel):
    id: str
    phone: str
    username: str
    password_hash: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserPublic(BaseModel):
    id: str
    phone: str
    username: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=1, max_length=11)
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=256)
    confirm_password: str = Field(..., min_length=1, max_length=256)
    code: Optional[str] = Field(default=None, max_length=64)


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=256)


class LoginResponse(BaseModel):
    token: str
    user: UserPublic
