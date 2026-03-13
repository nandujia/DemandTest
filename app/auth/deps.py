from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.tokens import decode_token
from app.models.user import UserRecord
from app.services.user_service import user_service


_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UserRecord:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("missing sub")
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="登录态无效")
