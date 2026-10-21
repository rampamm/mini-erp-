from typing import Annotated

import psycopg
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from siam_bean_erp.db import get_conn
from siam_bean_erp.security import decode_token

Conn = Annotated[psycopg.Connection, Depends(get_conn)]
_bearer = HTTPBearer(auto_error=False)


def current_user(
    conn: Conn,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict:
    if credentials is None:
        raise HTTPException(401, "Please log in")
    user_id = decode_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(401, "Your session has expired. Please log in again")
    try:
        user = conn.execute(
            "select id, email, full_name, role, active from profiles where id = %s", (user_id,)
        ).fetchone()
    except psycopg.errors.InvalidTextRepresentation:
        user = None
    if user is None or not user["active"]:
        raise HTTPException(401, "Your session has expired. Please log in again")
    return user


User = Annotated[dict, Depends(current_user)]


def require_roles(*roles: str):
    def check(user: User) -> dict:
        if user["role"] not in roles:
            raise HTTPException(403, "Your role is not allowed to do this")
        return user

    return Depends(check)
