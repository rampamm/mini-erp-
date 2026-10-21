from datetime import datetime
from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from siam_bean_erp.deps import Conn, require_roles
from siam_bean_erp.errors import db_message

router = APIRouter(prefix="/api/stock", tags=["stock"], dependencies=[require_roles("admin", "warehouse")])


class MovementOut(BaseModel):
    id: int
    product_id: UUID
    sku: str
    movement_type: str
    quantity: int
    reason: str | None
    user_name: str
    created_at: datetime


class StockIn(BaseModel):
    product_id: UUID
    quantity: int
    note: str | None = None

    @field_validator("quantity")
    @classmethod
    def above_zero(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Quantity must be above 0")
        return value


class Adjustment(BaseModel):
    product_id: UUID
    quantity: int
    reason: str

    @field_validator("quantity")
    @classmethod
    def not_zero(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Quantity cannot be 0")
        return value

    @field_validator("reason")
    @classmethod
    def reason_present(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Reason is required")
        return value.strip()


MOVEMENT_SELECT = (
    "select m.id, m.product_id, p.sku, m.movement_type, m.quantity, m.reason,"
    " u.full_name as user_name, m.created_at"
    " from stock_movements m join products p on p.id = m.product_id join profiles u on u.id = m.user_id"
)


def _record(conn: psycopg.Connection, user: dict, product_id: UUID, kind: str, quantity: int, reason: str | None):
    if conn.execute("select 1 from products where id = %s", (product_id,)).fetchone() is None:
        raise HTTPException(404, "Product not found")
    try:
        with conn.transaction():
            movement = conn.execute(
                "insert into stock_movements (product_id, movement_type, quantity, reason, user_id)"
                " values (%s, %s, %s, %s, %s) returning id",
                (product_id, kind, quantity, reason, user["id"]),
            ).fetchone()
    except psycopg.errors.RaiseException as error:
        raise HTTPException(409, db_message(error)) from None
    return conn.execute(f"{MOVEMENT_SELECT} where m.id = %s", (movement["id"],)).fetchone()


@router.post("/in", status_code=201, response_model=MovementOut)
def record_stock_in(body: StockIn, conn: Conn, user: Annotated[dict, require_roles("admin", "warehouse")]) -> dict:
    return _record(conn, user, body.product_id, "stock_in", body.quantity, body.note)


@router.post("/adjustments", status_code=201, response_model=MovementOut)
def record_adjustment(body: Adjustment, conn: Conn, user: Annotated[dict, require_roles("admin", "warehouse")]) -> dict:
    return _record(conn, user, body.product_id, "adjustment", body.quantity, body.reason)


@router.get("/movements", response_model=list[MovementOut])
def list_movements(conn: Conn, product_id: UUID | None = None, limit: int = 100) -> list[dict]:
    return conn.execute(
        f"{MOVEMENT_SELECT} where (%s::uuid is null or m.product_id = %s) order by m.id desc limit %s",
        (product_id, product_id, min(max(limit, 1), 500)),
    ).fetchall()
