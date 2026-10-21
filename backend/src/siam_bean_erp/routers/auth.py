from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from siam_bean_erp.deps import Conn, User
from siam_bean_erp.security import create_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(body: LoginRequest, conn: Conn) -> dict:
    user = conn.execute(
        "select id, email, full_name, role, active, password_hash from profiles where lower(email) = lower(%s)",
        (body.email.strip(),),
    ).fetchone()
    if user is None or not user["active"] or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Wrong email or password")
    user.pop("password_hash")
    return {"access_token": create_token(user["id"]), "user": user}


@router.get("/me")
def me(user: User) -> dict:
    return user
