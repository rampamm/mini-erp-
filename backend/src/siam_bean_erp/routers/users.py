from typing import Literal
from uuid import UUID

import psycopg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from siam_bean_erp.deps import Conn, require_roles
from siam_bean_erp.security import hash_password

router = APIRouter(prefix="/api/users", tags=["users"], dependencies=[require_roles("admin")])

Role = Literal["admin", "sales", "warehouse", "accountant"]
COLUMNS = "id, email, full_name, role, active"


class UserCreate(BaseModel):
    email: str
    full_name: str
    role: Role
    password: str

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip()
        if "@" not in value or value.startswith("@") or value.endswith("@") or " " in value:
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("full_name")
    @classmethod
    def name_present(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name is required")
        return value.strip()

    @field_validator("password")
    @classmethod
    def password_long_enough(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserUpdate(BaseModel):
    role: Role | None = None
    active: bool | None = None
    full_name: str | None = None


@router.get("")
def list_users(conn: Conn) -> list[dict]:
    return conn.execute(f"select {COLUMNS} from profiles order by full_name, email").fetchall()


@router.post("", status_code=201)
def create_user(body: UserCreate, conn: Conn) -> dict:
    try:
        with conn.transaction():
            return conn.execute(
                f"insert into profiles (email, full_name, role, password_hash)"
                f" values (%s, %s, %s, %s) returning {COLUMNS}",
                (body.email, body.full_name, body.role, hash_password(body.password)),
            ).fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, "A user with this email already exists") from None


@router.patch("/{user_id}")
def update_user(user_id: UUID, body: UserUpdate, conn: Conn) -> dict:
    with conn.transaction():
        user = conn.execute(
            f"update profiles set role = coalesce(%s, role), active = coalesce(%s, active),"
            f" full_name = coalesce(%s, full_name) where id = %s returning {COLUMNS}",
            (body.role, body.active, body.full_name, user_id),
        ).fetchone()
    if user is None:
        raise HTTPException(404, "User not found")
    return user
