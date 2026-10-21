from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

import psycopg
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, field_validator

from siam_bean_erp.deps import Conn, require_roles
from siam_bean_erp.schemas import Money

router = APIRouter(prefix="/api/orders", tags=["orders"], dependencies=[require_roles("admin", "sales")])

Seller = Annotated[dict, require_roles("admin", "sales")]


class CustomerRef(BaseModel):
    id: UUID
    name: str
    tax_id: str
    payment_terms: str


class LineOut(BaseModel):
    product_id: UUID
    sku: str
    name: str
    unit: str
    quantity: int
    unit_price: Money
    line_total: Money
    on_hand: int


class OrderOut(BaseModel):
    id: UUID
    number: str | None
    status: Literal["draft", "confirmed"]
    customer: CustomerRef
    lines: list[LineOut]
    subtotal: Money
    vat: Money
    total: Money
    created_at: datetime
    confirmed_at: datetime | None
    invoice_id: UUID | None
    invoice_number: str | None


class OrderSummary(BaseModel):
    id: UUID
    number: str | None
    status: Literal["draft", "confirmed"]
    customer_name: str
    total: Money
    created_at: datetime


class LineIn(BaseModel):
    product_id: UUID
    quantity: int

    @field_validator("quantity")
    @classmethod
    def above_zero(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Quantity must be above 0")
        return value


class OrderIn(BaseModel):
    customer_id: UUID
    lines: list[LineIn] = []


def load_order(conn: psycopg.Connection, order_id: UUID) -> dict | None:
    order = conn.execute(
        "select o.id, o.number, o.status, o.created_at, o.confirmed_at,"
        " c.id as customer_id, c.name as customer_name, c.tax_id, c.payment_terms,"
        " i.id as invoice_id, i.number as invoice_number"
        " from sales_orders o join customers c on c.id = o.customer_id"
        " left join invoices i on i.sales_order_id = o.id where o.id = %s",
        (order_id,),
    ).fetchone()
    if order is None:
        return None
    lines = conn.execute(
        "select l.product_id, p.sku, p.name, p.unit, l.quantity, l.unit_price,"
        " l.quantity * l.unit_price as line_total, s.on_hand"
        " from sales_order_lines l join products p on p.id = l.product_id"
        " join product_stock s on s.product_id = p.id where l.order_id = %s order by p.sku",
        (order_id,),
    ).fetchall()
    subtotal = sum((line["line_total"] for line in lines), Decimal(0))
    vat = conn.execute("select calc_vat(%s) as v", (subtotal,)).fetchone()["v"]
    return {
        "id": order["id"],
        "number": order["number"],
        "status": order["status"],
        "customer": {
            "id": order["customer_id"],
            "name": order["customer_name"],
            "tax_id": order["tax_id"],
            "payment_terms": order["payment_terms"],
        },
        "lines": lines,
        "subtotal": subtotal,
        "vat": vat,
        "total": subtotal + vat,
        "created_at": order["created_at"],
        "confirmed_at": order["confirmed_at"],
        "invoice_id": order["invoice_id"],
        "invoice_number": order["invoice_number"],
    }


def _require_draft(conn: psycopg.Connection, order_id: UUID) -> None:
    order = conn.execute("select status from sales_orders where id = %s for update", (order_id,)).fetchone()
    if order is None:
        raise HTTPException(404, "Order not found")
    if order["status"] != "draft":
        raise HTTPException(409, "A confirmed order cannot be changed")


def _check_customer(conn: psycopg.Connection, customer_id: UUID) -> None:
    customer = conn.execute("select name, active from customers where id = %s", (customer_id,)).fetchone()
    if customer is None:
        raise HTTPException(404, "Customer not found")
    if not customer["active"]:
        raise HTTPException(409, f"Customer {customer['name']} is deactivated")


def _save_lines(conn: psycopg.Connection, order_id: UUID, lines: list[LineIn]) -> None:
    wanted: dict[UUID, int] = {}
    for line in lines:
        wanted[line.product_id] = wanted.get(line.product_id, 0) + line.quantity
    kept_prices = {
        row["product_id"]: row["unit_price"]
        for row in conn.execute("select product_id, unit_price from sales_order_lines where order_id = %s", (order_id,))
    }
    rows = []
    for product_id, quantity in wanted.items():
        product = conn.execute("select sku, price, active from products where id = %s", (product_id,)).fetchone()
        if product is None:
            raise HTTPException(404, "Product not found")
        if not product["active"]:
            raise HTTPException(409, f"Product {product['sku']} is deactivated")
        rows.append((order_id, product_id, quantity, kept_prices.get(product_id, product["price"])))
    conn.execute("delete from sales_order_lines where order_id = %s", (order_id,))
    for row in rows:
        conn.execute(
            "insert into sales_order_lines (order_id, product_id, quantity, unit_price) values (%s, %s, %s, %s)", row
        )


@router.get("", response_model=list[OrderSummary])
def list_orders(conn: Conn, status: Literal["draft", "confirmed"] | None = None) -> list[dict]:
    return conn.execute(
        "select o.id, o.number, o.status, c.name as customer_name, o.created_at,"
        " t.subtotal + calc_vat(t.subtotal) as total"
        " from sales_orders o join customers c on c.id = o.customer_id"
        " cross join lateral (select coalesce(sum(quantity * unit_price), 0) as subtotal"
        "   from sales_order_lines where order_id = o.id) t"
        " where (%s::text is null or o.status = %s) order by o.created_at desc, o.id",
        (status, status),
    ).fetchall()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: UUID, conn: Conn) -> dict:
    order = load_order(conn, order_id)
    if order is None:
        raise HTTPException(404, "Order not found")
    return order


@router.post("", status_code=201, response_model=OrderOut)
def create_order(body: OrderIn, conn: Conn, user: Seller) -> dict:
    _check_customer(conn, body.customer_id)
    with conn.transaction():
        order_id = conn.execute(
            "insert into sales_orders (customer_id, created_by) values (%s, %s) returning id",
            (body.customer_id, user["id"]),
        ).fetchone()["id"]
        _save_lines(conn, order_id, body.lines)
    return load_order(conn, order_id)


@router.put("/{order_id}", response_model=OrderOut)
def replace_draft(order_id: UUID, body: OrderIn, conn: Conn) -> dict:
    with conn.transaction():
        _require_draft(conn, order_id)
        _check_customer(conn, body.customer_id)
        conn.execute("update sales_orders set customer_id = %s where id = %s", (body.customer_id, order_id))
        _save_lines(conn, order_id, body.lines)
    return load_order(conn, order_id)


@router.delete("/{order_id}", status_code=204)
def delete_draft(order_id: UUID, conn: Conn) -> Response:
    with conn.transaction():
        _require_draft(conn, order_id)
        conn.execute("delete from sales_orders where id = %s", (order_id,))
    return Response(status_code=204)
