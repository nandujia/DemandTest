from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re

from app.core.config import settings


_PHONE_RE = re.compile(r"^\d{1,11}$")


def validate_phone(phone: str) -> bool:
    return bool(phone) and bool(_PHONE_RE.fullmatch(phone))


def validate_password(password: str) -> bool:
    if not password:
        return False
    if settings.AUTH_ALLOW_TEST_DEFAULT_PASSWORD and password == settings.AUTH_TEST_DEFAULT_PASSWORD:
        return True
    if len(password) < 8 or len(password) > 16:
        return False
    has_upper = any("A" <= c <= "Z" for c in password)
    has_lower = any("a" <= c <= "z" for c in password)
    has_letter = has_upper or has_lower
    has_special = any(not c.isalnum() for c in password)
    return has_letter and ((has_upper and has_lower) or has_special)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    iterations = 200_000
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256$%d$%s$%s" % (
        iterations,
        base64.urlsafe_b64encode(salt).decode("utf-8").rstrip("="),
        base64.urlsafe_b64encode(dk).decode("utf-8").rstrip("="),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algo, iters_s, salt_s, dk_s = stored_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iters_s)
        salt = base64.urlsafe_b64decode(_pad_b64(salt_s))
        expected = base64.urlsafe_b64decode(_pad_b64(dk_s))
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def _pad_b64(s: str) -> str:
    return s + "=" * (-len(s) % 4)
