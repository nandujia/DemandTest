from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.deps import get_current_user
from app.models.user import UserRecord
from app.services.user_service import user_service


class AdminUserItem(BaseModel):
    username: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


router = APIRouter()


@router.get("/admin/users", response_model=List[AdminUserItem])
async def list_users(_: UserRecord = Depends(get_current_user)):
    users = user_service.list_users()
    return [
        AdminUserItem(username=u.username, created_at=u.created_at, last_login_at=u.last_login_at)
        for u in users
    ]
