from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from siam_bean_erp.deps import Conn, require_roles
from siam_bean_erp.schemas import Money

router = APIRouter(prefix="/api/invoices", tags=["invoices"], dependencies=[require_roles("admin", "sales", "accountant")])
accounting = APIRouter(prefix="/api/accounting", tags=["accounting"], dependencies=[require_roles("admin", "accountant")])

InvoiceStatus = Literal["open", "partially_paid", "paid"]

SUMMARY_SELECT = (
    "select s.id, s.number, o.number as order_number, s.customer_name, s.issue_date, s.due_date,"
    " s.total, s.paid, s.balance, s.status, s.overdue"
    " from invoice_summary s join sales_orders o on o.id = s.sales_order_id"
)

DETAIL_SELECT = (
    "select s.id, s.number, o.number as order_number, s.customer_name, s.customer_tax_id, s.payment_terms,"
    " s.issue_date, s.due_date, s.subtotal, s.vat, s.total, s.paid, s.balance, s.status, s.overdue"
    " from invoice_summary s join sales_orders o on o.id = s.sales_order_id"
)


class InvoiceSummary(BaseModel):
    id: UUID
    number: str
    order_number: str
    customer_name: str
    issue_date: date
    due_date: date
    total: Money
    paid: Money
    balance: Money
    status: InvoiceStatus
    overdue: bool


class CustomerSnapshot(BaseModel):
    name: str
    tax_id: str
    payment_terms: str


class InvoiceLineOut(BaseModel):
    sku: str
    name: str
    unit: str
    quantity: int
    unit_price: Money
    line_total: Money


class PaymentOut(BaseModel):
    id: UUID
    invoice_id: UUID
    amount: Money
    paid_on: date
    recorded_by: str
    created_at: datetime


class InvoiceOut(InvoiceSummary):
    customer: CustomerSnapshot
    subtotal: Money
    vat: Money
    lines: list[InvoiceLineOut]
    payments: list[PaymentOut]


class Receivables(BaseModel):
    items: list[InvoiceSummary]
    total_open: Money


class PaymentIn(BaseModel):
    amount: Decimal
    paid_on: date | None = None

    @field_validator("amount")
    @classmethod
    def amount_ok(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("Amount must be a number")
        if value <= 0:
            raise ValueError("Amount must be above 0")
        if value != value.quantize(Decimal("0.01")):
            raise ValueError("Amount can have at most 2 decimals")
        return value


PAYMENT_SELECT = (
    "select p.id, p.invoice_id, p.amount, p.paid_on, u.full_name as recorded_by, p.created_at"
    " from payments p join profiles u on u.id = p.recorded_by"
)


@router.get("", response_model=list[InvoiceSummary])
def list_invoices(conn: Conn, status: InvoiceStatus | Literal["overdue"] | None = None) -> list[dict]:
    where = {None: "true", "overdue": "s.overdue"}.get(status, "s.status = %(status)s")
    return conn.execute(
        f"{SUMMARY_SELECT} where {where} order by s.issue_date desc, s.number desc", {"status": status}
    ).fetchall()


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: UUID, conn: Conn) -> dict:
    invoice = conn.execute(f"{DETAIL_SELECT} where s.id = %s", (invoice_id,)).fetchone()
    if invoice is None:
        raise HTTPException(404, "Invoice not found")
    lines = conn.execute(
        "select sku, name, unit, quantity, unit_price, line_total from invoice_lines"
        " where invoice_id = %s order by sku",
        (invoice_id,),
    ).fetchall()
    payments = conn.execute(f"{PAYMENT_SELECT} where p.invoice_id = %s order by p.seq", (invoice_id,)).fetchall()
    return {
        **invoice,
        "customer": {
            "name": invoice["customer_name"],
            "tax_id": invoice["customer_tax_id"],
            "payment_terms": invoice["payment_terms"],
        },
        "lines": lines,
        "payments": payments,
    }


@router.post(
    "/{invoice_id}/payments",
    status_code=201,
    response_model=PaymentOut,
    dependencies=[require_roles("admin", "accountant")],
)
def record_payment(
    invoice_id: UUID, body: PaymentIn, conn: Conn, user: Annotated[dict, require_roles("admin", "accountant")]
) -> dict:
    with conn.transaction():
        if conn.execute("select 1 from invoices where id = %s for update", (invoice_id,)).fetchone() is None:
            raise HTTPException(404, "Invoice not found")
        balance = conn.execute("select balance from invoice_summary where id = %s", (invoice_id,)).fetchone()["balance"]
        if balance == 0:
            raise HTTPException(409, "This invoice is already paid")
        if body.amount > balance:
            raise HTTPException(409, f"Payment is more than the balance of {balance:,.2f} THB")
        payment = conn.execute(
            "insert into payments (invoice_id, amount, paid_on, recorded_by)"
            " values (%s, %s, coalesce(%s, (now() at time zone 'Asia/Bangkok')::date), %s) returning id",
            (invoice_id, body.amount, body.paid_on, user["id"]),
        ).fetchone()
    return conn.execute(f"{PAYMENT_SELECT} where p.id = %s", (payment["id"],)).fetchone()


@accounting.get("/receivables", response_model=Receivables)
def receivables(conn: Conn) -> dict:
    items = conn.execute(f"{SUMMARY_SELECT} where s.balance > 0 order by s.due_date, s.number").fetchall()
    return {"items": items, "total_open": sum((i["balance"] for i in items), Decimal(0))}
