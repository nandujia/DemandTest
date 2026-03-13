from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import HTTPException

from app.auth.passwords import hash_password, validate_password, validate_phone, verify_password
from app.core.config import settings
from app.models.user import UserPublic, UserRecord


class UserService:
    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or (settings.get_storage_path("data") / "users.json")

    def list_users(self) -> List[UserPublic]:
        users = self._load()
        items = sorted(users.values(), key=lambda u: u.created_at, reverse=True)
        return [self._to_public(u) for u in items]

    def get_user(self, user_id: str) -> Optional[UserRecord]:
        users = self._load()
        return users.get(user_id)

    def create_user(self, phone: str, username: str, password: str) -> UserPublic:
        phone = (phone or "").strip()
        username = (username or "").strip()

        if not validate_phone(phone):
            raise HTTPException(status_code=400, detail="手机号格式不正确")
        if not username:
            raise HTTPException(status_code=400, detail="用户名不能为空")
        if not validate_password(password):
            raise HTTPException(status_code=400, detail="密码不符合规则")

        users = self._load()
        if any(u.phone == phone for u in users.values()):
            raise HTTPException(status_code=400, detail="手机号已注册")
        if any(u.username == username for u in users.values()):
            raise HTTPException(status_code=400, detail="用户名已存在")

        now = datetime.now(timezone.utc)
        user = UserRecord(
            id=str(uuid.uuid4()),
            phone=phone,
            username=username,
            password_hash=hash_password(password),
            created_at=now,
            last_login_at=None,
        )
        users[user.id] = user
        self._save(users)
        return self._to_public(user)

    def authenticate(self, identifier: str, password: str) -> UserPublic:
        identifier = (identifier or "").strip()
        if not identifier:
            raise HTTPException(status_code=400, detail="请输入用户名或手机号")
        users = self._load()
        user = next((u for u in users.values() if u.username == identifier or u.phone == identifier), None)
        if not user:
            raise HTTPException(status_code=400, detail="用户名或密码错误")
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=400, detail="用户名或密码错误")

        user.last_login_at = datetime.now(timezone.utc)
        users[user.id] = user
        self._save(users)
        return self._to_public(user)

    def _load(self) -> Dict[str, UserRecord]:
        if not self.storage_file.exists():
            return {}
        try:
            data = json.loads(self.storage_file.read_text(encoding="utf-8") or "[]")
            users: Dict[str, UserRecord] = {}
            for item in data:
                u = UserRecord.model_validate(item)
                users[u.id] = u
            return users
        except Exception:
            return {}

    def _save(self, users: Dict[str, UserRecord]) -> None:
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        items = [u.model_dump(mode="json") for u in users.values()]
        tmp = self.storage_file.with_suffix(self.storage_file.suffix + ".tmp")
        tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.storage_file)

    def _to_public(self, user: UserRecord) -> UserPublic:
        return UserPublic(
            id=user.id,
            phone=user.phone,
            username=user.username,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )


user_service = UserService()
