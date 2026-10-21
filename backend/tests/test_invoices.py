from datetime import timedelta

import psycopg
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


@pytest.fixture
def shop(client, h):
    arabica = make_product(client, h["admin"], "ARB-1KG", price="450")
    put_stock(client, h["warehouse"], arabica, 170)
    return {"arabica": arabica}


def issue(client, h, shop, customer, quantity=20):
    order = make_order(client, h["sales"], customer, [(shop["arabica"], quantity)])
    return confirm(client, h["sales"], order).json()


def invoice_of(client, h, order):
    return client.get(f"/api/invoices/{order['invoice_id']}", headers=h["sales"]).json()


def test_the_invoice_has_the_orders_lines_and_the_9630_total(client, h, shop):
    lune = make_customer(client, h["sales"], "Café Lune")
    order = issue(client, h, shop, lune)

    invoice = invoice_of(client, h, order)

    assert invoice["number"] == "INV-0001"
    assert invoice["order_number"] == "SO-0001"
    assert (invoice["subtotal"], invoice["vat"], invoice["total"]) == ("9000.00", "630.00", "9630.00")
    assert [(l["sku"], l["quantity"], l["unit_price"], l["line_total"]) for l in invoice["lines"]] == [
        ("ARB-1KG", 20, "450.00", "9000.00")
    ]
    assert (invoice["paid"], invoice["balance"], invoice["status"], invoice["overdue"]) == (
        "0.00", "9630.00", "open", False,
    )
    assert invoice["payments"] == []


def test_the_invoice_keeps_the_customer_details_from_the_day_it_was_issued(client, h, shop):
    lune = make_customer(client, h["sales"], "Café Lune", "30 days", "0105561000011")
    order = issue(client, h, shop, lune)

    client.patch(
        f"/api/customers/{lune['id']}",
        json={"name": "Renamed Café", "tax_id": "9999999999999", "payment_terms": "Cash"},
        headers=h["sales"],
    )

    invoice = invoice_of(client, h, order)
    assert invoice["customer"] == {"name": "Café Lune", "tax_id": "0105561000011", "payment_terms": "30 days"}


@pytest.mark.parametrize("terms,days", [("Cash", 0), ("15 days", 15), ("30 days", 30)])
def test_the_due_date_follows_the_payment_terms(client, h, shop, terms, days):
    customer = make_customer(client, h["sales"], f"Café {terms}", terms, "0105561000099")
    order = issue(client, h, shop, customer, 1)

    invoice = invoice_of(client, h, order)

    today = today_in_bangkok()
    assert invoice["issue_date"] == today.isoformat()
    assert invoice["due_date"] == (today + timedelta(days=days)).isoformat()


def test_the_list_shows_what_the_accountant_needs(client, h, shop):
    lune = make_customer(client, h["sales"], "Café Lune")
    issue(client, h, shop, lune)

    rows = client.get("/api/invoices", headers=h["accountant"]).json()

    assert len(rows) == 1
    row = rows[0]
    assert (row["number"], row["customer_name"], row["total"], row["balance"], row["status"]) == (
        "INV-0001", "Café Lune", "9630.00", "9630.00", "open",
    )
    assert row["due_date"] and row["order_number"] == "SO-0001"


def test_the_list_can_be_filtered_by_status(client, h, shop):
    lune = make_customer(client, h["sales"], "Café Lune")
    first = issue(client, h, shop, lune, 1)
    second = issue(client, h, shop, lune, 1)
    third = issue(client, h, shop, lune, 1)
    pay(client, h["accountant"], first["invoice_id"], "100.00")
    pay(client, h["accountant"], second["invoice_id"], "481.50")

    def numbers(status):
        rows = client.get(f"/api/invoices?status={status}", headers=h["accountant"]).json()
        return [r["number"] for r in rows]

    assert numbers("open") == [third["invoice_number"]]
    assert numbers("partially_paid") == [first["invoice_number"]]
    assert numbers("paid") == [second["invoice_number"]]


def test_an_unpaid_invoice_past_its_due_date_is_overdue_and_stops_being_overdue_when_paid(client, h, shop, conn):
    lune = make_customer(client, h["sales"], "Café Lune")
    order = issue(client, h, shop, lune)
    backdate_due_date(conn, order["invoice_id"], today_in_bangkok() - timedelta(days=1))

    overdue = client.get("/api/invoices?status=overdue", headers=h["accountant"]).json()
    assert [r["number"] for r in overdue] == ["INV-0001"]
    assert overdue[0]["overdue"] is True and overdue[0]["status"] == "open"

    pay(client, h["accountant"], order["invoice_id"], "9630.00")

    assert client.get("/api/invoices?status=overdue", headers=h["accountant"]).json() == []


def test_an_invoice_due_today_is_not_overdue_yet(client, h, shop):
    cash = make_customer(client, h["sales"], "Brew Lab Ari", "Cash", "0105562000022")
    issue(client, h, shop, cash, 1)

    assert client.get("/api/invoices?status=overdue", headers=h["accountant"]).json() == []


def test_with_no_invoices_the_list_is_empty(client, h):
    assert client.get("/api/invoices", headers=h["accountant"]).json() == []


def test_an_unknown_invoice_is_a_404(client, h):
    response = client.get("/api/invoices/00000000-0000-0000-0000-000000000000", headers=h["accountant"])

    assert response.status_code == 404


@pytest.mark.parametrize("role,expected", [("admin", 200), ("sales", 200), ("accountant", 200), ("warehouse", 403)])
def test_who_can_see_invoices(client, h, shop, role, expected):
    lune = make_customer(client, h["sales"], "Café Lune")
    order = issue(client, h, shop, lune, 1)

    assert client.get("/api/invoices", headers=h[role]).status_code == expected
    assert client.get(f"/api/invoices/{order['invoice_id']}", headers=h[role]).status_code == expected


def test_an_issued_invoice_cannot_be_changed_even_directly_in_the_database(client, h, shop, conn):
    lune = make_customer(client, h["sales"], "Café Lune")
    order = issue(client, h, shop, lune)

    with pytest.raises(psycopg.errors.RaiseException):
        conn.execute("update invoices set total = 1 where id = %s", (order["invoice_id"],))
