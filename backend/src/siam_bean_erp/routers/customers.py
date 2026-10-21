import re
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator

from siam_bean_erp.deps import Conn, require_roles

router = APIRouter(prefix="/api/customers", tags=["customers"])

PAGE_SIZE = 20
COLUMNS = "id, name, tax_id, payment_terms, active"
PaymentTerms = Literal["Cash", "15 days", "30 days"]

can_view = require_roles("admin", "sales", "accountant")
can_edit = require_roles("admin", "sales")


class CustomerOut(BaseModel):
    id: UUID
    name: str
    tax_id: str
    payment_terms: PaymentTerms
    active: bool


class CustomerPage(BaseModel):
    items: list[CustomerOut]
    total: int
    page: int
    page_size: int


def _name(value: str | None) -> str | None:
    if value is None:
        return None
    if not value.strip():
        raise ValueError("Name is required")
    return value.strip()


def _tax_id(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        raise ValueError("Tax ID is required")
    if not re.fullmatch(r"[0-9]{13}", value):
        raise ValueError("Tax ID must be 13 digits")
    return value


class CustomerCreate(BaseModel):
    name: str
    tax_id: str
    payment_terms: PaymentTerms

    _name = field_validator("name")(_name)
    _tax_id = field_validator("tax_id")(_tax_id)


class CustomerUpdate(BaseModel):
    name: str | None = None
    tax_id: str | None = None
    payment_terms: PaymentTerms | None = None
    active: bool | None = None

    _name = field_validator("name")(_name)
    _tax_id = field_validator("tax_id")(_tax_id)


def _like_pattern(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


@router.get("", response_model=CustomerPage, dependencies=[can_view])
def search_customers(
    conn: Conn,
    q: str = "",
    page: Annotated[int, Query(ge=1)] = 1,
    active: bool | None = None,
) -> dict:
    where = "(name ilike %s escape '\\') and (%s::boolean is null or active = %s)"
    params = (_like_pattern(q.strip()), active, active)
    total = conn.execute(f"select count(*) as n from customers where {where}", params).fetchone()["n"]
    items = conn.execute(
        f"select {COLUMNS} from customers where {where} order by lower(name), id limit %s offset %s",
        (*params, PAGE_SIZE, (page - 1) * PAGE_SIZE),
    ).fetchall()
    return {"items": items, "total": total, "page": page, "page_size": PAGE_SIZE}


@router.get("/{customer_id}", response_model=CustomerOut, dependencies=[can_view])
def get_customer(customer_id: UUID, conn: Conn) -> dict:
    customer = conn.execute(f"select {COLUMNS} from customers where id = %s", (customer_id,)).fetchone()
    if customer is None:
        raise HTTPException(404, "Customer not found")
    return customer


@router.post("", status_code=201, response_model=CustomerOut, dependencies=[can_edit])
def create_customer(body: CustomerCreate, conn: Conn) -> dict:
    with conn.transaction():
        return conn.execute(
            f"insert into customers (name, tax_id, payment_terms) values (%s, %s, %s) returning {COLUMNS}",
            (body.name, body.tax_id, body.payment_terms),
        ).fetchone()


@router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: UUID, body: CustomerUpdate, conn: Conn, user: Annotated[dict, can_edit]) -> dict:
    current = conn.execute("select active from customers where id = %s", (customer_id,)).fetchone()
    if current is None:
        raise HTTPException(404, "Customer not found")
    if body.active is True and not current["active"] and user["role"] != "admin":
        raise HTTPException(403, "Only an Admin can reactivate a customer")
    with conn.transaction():
        return conn.execute(
            f"update customers set name = coalesce(%s, name), tax_id = coalesce(%s, tax_id),"
            f" payment_terms = coalesce(%s, payment_terms), active = coalesce(%s, active)"
            f" where id = %s returning {COLUMNS}",
            (body.name, body.tax_id, body.payment_terms, body.active, customer_id),
        ).fetchone()
