import re
from decimal import Decimal
from uuid import UUID

import psycopg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from siam_bean_erp.deps import Conn, User, require_roles
from siam_bean_erp.schemas import Money, check_money

router = APIRouter(prefix="/api/products", tags=["products"])

COLUMNS = "id, sku, name, unit, cost, price, reorder_level, active"


class ProductOut(BaseModel):
    id: UUID
    sku: str
    name: str
    unit: str
    cost: Money
    price: Money
    reorder_level: int
    active: bool


def _sku(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("SKU is required")
    if not re.fullmatch(r"[A-Z0-9-]+", value):
        raise ValueError("SKU can only use capital letters, digits and hyphens")
    return value


def _required(value: str, message: str) -> str:
    if not value.strip():
        raise ValueError(message)
    return value.strip()


class ProductCreate(BaseModel):
    sku: str
    name: str
    unit: str
    cost: Decimal
    price: Decimal
    reorder_level: int = 0

    _sku = field_validator("sku")(_sku)

    @field_validator("name")
    @classmethod
    def name_present(cls, value: str) -> str:
        return _required(value, "Name is required")

    @field_validator("unit")
    @classmethod
    def unit_present(cls, value: str) -> str:
        return _required(value, "Unit is required")

    @field_validator("cost")
    @classmethod
    def cost_ok(cls, value: Decimal) -> Decimal:
        return check_money(value, "Cost")

    @field_validator("price")
    @classmethod
    def price_ok(cls, value: Decimal) -> Decimal:
        return check_money(value, "Price")

    @field_validator("reorder_level")
    @classmethod
    def reorder_ok(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Reorder level cannot be below 0")
        return value


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    unit: str | None = None
    cost: Decimal | None = None
    price: Decimal | None = None
    reorder_level: int | None = None
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def name_present(cls, value: str | None) -> str | None:
        return None if value is None else _required(value, "Name is required")

    @field_validator("unit")
    @classmethod
    def unit_present(cls, value: str | None) -> str | None:
        return None if value is None else _required(value, "Unit is required")

    @field_validator("cost")
    @classmethod
    def cost_ok(cls, value: Decimal | None) -> Decimal | None:
        return None if value is None else check_money(value, "Cost")

    @field_validator("price")
    @classmethod
    def price_ok(cls, value: Decimal | None) -> Decimal | None:
        return None if value is None else check_money(value, "Price")

    @field_validator("reorder_level")
    @classmethod
    def reorder_ok(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("Reorder level cannot be below 0")
        return value


@router.get("", response_model=list[ProductOut])
def list_products(conn: Conn, _: User, active: bool | None = None) -> list[dict]:
    return conn.execute(
        f"select {COLUMNS} from products where (%s::boolean is null or active = %s) order by sku",
        (active, active),
    ).fetchall()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, conn: Conn, _: User) -> dict:
    product = conn.execute(f"select {COLUMNS} from products where id = %s", (product_id,)).fetchone()
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


@router.post("", status_code=201, response_model=ProductOut, dependencies=[require_roles("admin")])
def create_product(body: ProductCreate, conn: Conn) -> dict:
    try:
        with conn.transaction():
            return conn.execute(
                f"insert into products (sku, name, unit, cost, price, reorder_level)"
                f" values (%s, %s, %s, %s, %s, %s) returning {COLUMNS}",
                (body.sku, body.name, body.unit, body.cost, body.price, body.reorder_level),
            ).fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, "SKU already exists") from None


@router.patch("/{product_id}", response_model=ProductOut, dependencies=[require_roles("admin")])
def update_product(product_id: UUID, body: ProductUpdate, conn: Conn) -> dict:
    current = conn.execute("select sku from products where id = %s", (product_id,)).fetchone()
    if current is None:
        raise HTTPException(404, "Product not found")
    if body.sku is not None and body.sku != current["sku"]:
        raise HTTPException(422, "SKU cannot be changed")
    with conn.transaction():
        return conn.execute(
            f"update products set name = coalesce(%s, name), unit = coalesce(%s, unit),"
            f" cost = coalesce(%s, cost), price = coalesce(%s, price),"
            f" reorder_level = coalesce(%s, reorder_level), active = coalesce(%s, active)"
            f" where id = %s returning {COLUMNS}",
            (body.name, body.unit, body.cost, body.price, body.reorder_level, body.active, product_id),
        ).fetchone()
