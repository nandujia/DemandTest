from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict

from app.core.config import settings


def create_access_token(user_id: str, username: str) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "username": username,
        "iat": now,
        "exp": now + int(settings.AUTH_TOKEN_EXPIRE_SECONDS),
    }
    return _encode(header, payload, settings.AUTH_SECRET_KEY)


def decode_token(token: str) -> Dict[str, Any]:
    header, payload = _decode(token, settings.AUTH_SECRET_KEY)
    exp = int(payload.get("exp", 0))
    if exp and int(time.time()) > exp:
        raise ValueError("token expired")
    return payload


def _encode(header: Dict[str, Any], payload: Dict[str, Any], secret: str) -> str:
    header_b = _b64url(json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    payload_b = _b64url(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    signing_input = f"{header_b}.{payload_b}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b = _b64url(sig)
    return f"{header_b}.{payload_b}.{sig_b}"


def _decode(token: str, secret: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid token")
    header_b, payload_b, sig_b = parts
    signing_input = f"{header_b}.{payload_b}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual = _b64url_decode(sig_b)
    if not hmac.compare_digest(expected, actual):
        raise ValueError("invalid signature")
    header = json.loads(_b64url_decode(header_b).decode("utf-8"))
    payload = json.loads(_b64url_decode(payload_b).decode("utf-8"))
    return header, payload


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
