import hashlib
import hmac
import os
import time
from uuid import UUID

import jwt

from siam_bean_erp.settings import get_settings

AUDIENCE = "authenticated"


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        _, salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_token(user_id: UUID | str) -> str:
    settings = get_settings()
    now = int(time.time())
    claims = {
        "sub": str(user_id),
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + settings.token_ttl_hours * 3600,
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> str | None:
    """Return the user id the token was issued for, or None if it is invalid or expired."""
    try:
        claims = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"], audience=AUDIENCE)
    except jwt.PyJWTError:
        return None
    return claims.get("sub")
