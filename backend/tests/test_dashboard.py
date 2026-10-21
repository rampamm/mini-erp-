from datetime import timedelta

import pytest
from helpers import (
    backdate_due_date,
    confirm,
    make_customer,
    make_order,
    make_product,
    pay,
    put_stock,
    today_in_bangkok,
)

from siam_bean_erp.seed import seed


def dashboard(client, headers):
    response = client.get("/api/dashboard", headers=headers)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def shop(client, h):
    arabica = make_product(client, h["admin"], "ARB-1KG", price="450")
    put_stock(client, h["warehouse"], arabica, 170)
    lune = make_customer(client, h["sales"], "Café Lune")
    return {"arabica": arabica, "lune": lune}


def sell(client, h, shop, quantity=20):
    return confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], [(shop["arabica"], quantity)])).json()


def test_an_empty_system_shows_zeros(client, h):
    assert dashboard(client, h["admin"]) == {
        "sales_today": "0.00",
        "low_stock_count": 0,
        "open_receivables": "0.00",
        "open_invoices": 0,
    }


def test_sales_today_is_the_invoice_subtotal_excluding_vat(client, h, shop):
    sell(client, h, shop, 20)

    assert dashboard(client, h["admin"])["sales_today"] == "9000.00"


def test_invoices_issued_on_an_earlier_bangkok_day_do_not_count_as_today(client, h, shop, conn):
    order = sell(client, h, shop, 20)
    conn.execute("alter table invoices disable trigger invoices_immutable")
    conn.execute(
        "update invoices set issue_date = %s where id = %s", (today_in_bangkok() - timedelta(days=1), order["invoice_id"])
    )
    conn.execute("alter table invoices enable trigger invoices_immutable")

    assert dashboard(client, h["admin"])["sales_today"] == "0.00"


def test_open_receivables_include_vat_and_drop_when_the_invoice_is_paid(client, h, shop):
    order = sell(client, h, shop, 20)
    assert dashboard(client, h["admin"])["open_receivables"] == "9630.00"

    pay(client, h["accountant"], order["invoice_id"], "9630.00")

    after = dashboard(client, h["admin"])
    assert (after["open_receivables"], after["open_invoices"]) == ("0.00", 0)


def test_a_partly_paid_invoice_is_still_open(client, h, shop):
    order = sell(client, h, shop, 20)
    pay(client, h["accountant"], order["invoice_id"], "630.00")

    numbers = dashboard(client, h["admin"])

    assert (numbers["open_receivables"], numbers["open_invoices"]) == ("9000.00", 1)


def test_the_open_invoice_count_agrees_with_the_invoice_list(client, h, shop):
    sell(client, h, shop, 1)
    paid = sell(client, h, shop, 1)
    sell(client, h, shop, 1)
    pay(client, h["accountant"], paid["invoice_id"], "481.50")

    listed = [i for i in client.get("/api/invoices", headers=h["accountant"]).json() if i["status"] != "paid"]

    assert dashboard(client, h["admin"])["open_invoices"] == len(listed) == 2


def test_overdue_invoices_still_count_as_open(client, h, shop, conn):
    order = sell(client, h, shop, 1)
    backdate_due_date(conn, order["invoice_id"], today_in_bangkok() - timedelta(days=3))

    assert dashboard(client, h["admin"])["open_invoices"] == 1


def test_the_low_stock_count_matches_the_flags_on_the_product_list(client, h, conn):
    seed(conn)

    flagged = [p for p in client.get("/api/products?active=true", headers=h["sales"]).json() if p["low_stock"]]

    assert dashboard(client, h["sales"])["low_stock_count"] == len(flagged) == 1


def test_stock_in_that_lifts_a_product_out_of_low_stock_lowers_the_count(client, h, conn):
    seed(conn)
    robusta = next(p for p in client.get("/api/products", headers=h["admin"]).json() if p["sku"] == "ROB-1KG")

    put_stock(client, h["warehouse"], robusta, 5)

    assert dashboard(client, h["admin"])["low_stock_count"] == 0


def test_a_deactivated_product_is_not_counted_as_low_stock(client, h, conn):
    seed(conn)
    robusta = next(p for p in client.get("/api/products", headers=h["admin"]).json() if p["sku"] == "ROB-1KG")
    client.patch(f"/api/products/{robusta['id']}", json={"active": False}, headers=h["admin"])

    assert dashboard(client, h["admin"])["low_stock_count"] == 0


@pytest.mark.parametrize("role", ["admin", "sales", "warehouse", "accountant"])
def test_every_role_can_see_the_dashboard(client, h, role):
    assert client.get("/api/dashboard", headers=h[role]).status_code == 200


def test_the_dashboard_needs_a_login(client):
    assert client.get("/api/dashboard").status_code == 401
