from fastapi import APIRouter
from pydantic import BaseModel

from siam_bean_erp.deps import Conn, User
from siam_bean_erp.schemas import Money

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class Dashboard(BaseModel):
    sales_today: Money
    low_stock_count: int
    open_receivables: Money
    open_invoices: int


@router.get("", response_model=Dashboard)
def dashboard(conn: Conn, _: User) -> dict:
    return conn.execute(
        """
        select
            (select coalesce(sum(subtotal), 0) from invoices
              where issue_date = (now() at time zone 'Asia/Bangkok')::date) as sales_today,
            (select count(*) from products p join product_stock s on s.product_id = p.id
              where p.active and s.on_hand < p.reorder_level) as low_stock_count,
            (select coalesce(sum(balance), 0) from invoice_summary where balance > 0) as open_receivables,
            (select count(*) from invoice_summary where balance > 0) as open_invoices
        """
    ).fetchone()
