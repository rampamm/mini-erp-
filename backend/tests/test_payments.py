import psycopg
import pytest
from helpers import (
    confirm,
    make_customer,
    make_order,
    make_product,
    pay,
    put_stock,
    today_in_bangkok,
)


@pytest.fixture
def invoice(client, h):
    arabica = make_product(client, h["admin"], "ARB-1KG", price="450")
    put_stock(client, h["warehouse"], arabica, 170)
    lune = make_customer(client, h["sales"], "Café Lune")
    order = confirm(client, h["sales"], make_order(client, h["sales"], lune, [(arabica, 20)])).json()
    return order["invoice_id"]


def detail(client, h, invoice_id):
    return client.get(f"/api/invoices/{invoice_id}", headers=h["accountant"]).json()


def test_a_full_payment_marks_the_invoice_paid(client, h, invoice):
    response = pay(client, h["accountant"], invoice, "9630.00")

    assert response.status_code == 201
    after = detail(client, h, invoice)
    assert (after["status"], after["paid"], after["balance"]) == ("paid", "9630.00", "0.00")


def test_a_partial_payment_leaves_the_invoice_partially_paid_with_the_balance(client, h, invoice):
    pay(client, h["accountant"], invoice, "4000")

    after = detail(client, h, invoice)
    assert (after["status"], after["paid"], after["balance"]) == ("partially_paid", "4000.00", "5630.00")

    pay(client, h["accountant"], invoice, "5630")
    assert detail(client, h, invoice)["status"] == "paid"


def test_a_payment_larger_than_the_balance_is_refused_and_changes_nothing(client, h, invoice):
    response = pay(client, h["accountant"], invoice, "9631.00")

    assert response.status_code == 409
    assert response.json()["detail"] == "Payment is more than the balance of 9,630.00 THB"
    assert detail(client, h, invoice)["status"] == "open"


def test_paying_an_invoice_that_is_already_paid_is_refused(client, h, invoice):
    pay(client, h["accountant"], invoice, "9630.00")

    response = pay(client, h["accountant"], invoice, "1.00")

    assert response.status_code == 409
    assert response.json()["detail"] == "This invoice is already paid"


@pytest.mark.parametrize(
    "amount,message",
    [
        ("0", "Amount must be above 0"),
        ("-5", "Amount must be above 0"),
        ("abc", "Amount must be a number"),
        ("10.555", "Amount can have at most 2 decimals"),
    ],
)
def test_a_bad_amount_says_what_to_fix(client, h, invoice, amount, message):
    response = pay(client, h["accountant"], invoice, amount)

    assert response.status_code == 422
    assert response.json()["detail"] == message


def test_the_payment_date_defaults_to_today_and_can_be_given(client, h, invoice):
    first = pay(client, h["accountant"], invoice, "100.00").json()
    second = pay(client, h["accountant"], invoice, "200.00", paid_on="2026-10-01").json()

    assert first["paid_on"] == today_in_bangkok().isoformat()
    assert second["paid_on"] == "2026-10-01"


def test_the_invoice_lists_its_payments_oldest_first(client, h, invoice):
    pay(client, h["accountant"], invoice, "100.00")
    pay(client, h["accountant"], invoice, "250.50")

    payments = detail(client, h, invoice)["payments"]

    assert [p["amount"] for p in payments] == ["100.00", "250.50"]
    assert payments[0]["recorded_by"]


def test_a_payment_cannot_be_edited_or_deleted(client, h, invoice, conn):
    payment = pay(client, h["accountant"], invoice, "100.00").json()

    assert client.patch(f"/api/payments/{payment['id']}", json={"amount": "1"}, headers=h["admin"]).status_code == 404
    assert client.delete(f"/api/payments/{payment['id']}", headers=h["admin"]).status_code == 404
    with pytest.raises(psycopg.errors.RaiseException):
        conn.execute("update payments set amount = 1 where id = %s", (payment["id"],))


def test_paying_an_unknown_invoice_is_a_404(client, h):
    response = pay(client, h["accountant"], "00000000-0000-0000-0000-000000000000", "10")

    assert response.status_code == 404


@pytest.mark.parametrize("role,expected", [("admin", 201), ("accountant", 201), ("sales", 403), ("warehouse", 403)])
def test_who_can_record_payments(client, h, invoice, role, expected):
    assert pay(client, h[role], invoice, "10.00").status_code == expected


# ---- the Accounting screen --------------------------------------------------------------


def test_the_accounting_screen_is_closed_to_sales_and_warehouse(client, h):
    assert client.get("/api/accounting/receivables", headers=h["sales"]).status_code == 403
    assert client.get("/api/accounting/receivables", headers=h["warehouse"]).status_code == 403
    assert client.get("/api/accounting/receivables", headers=h["accountant"]).status_code == 200
    assert client.get("/api/accounting/receivables", headers=h["admin"]).status_code == 200


def test_receivables_lists_only_unpaid_invoices_with_what_is_still_owed(client, h, invoice):
    before = client.get("/api/accounting/receivables", headers=h["accountant"]).json()
    assert before["total_open"] == "9630.00"
    assert [(r["number"], r["balance"]) for r in before["items"]] == [("INV-0001", "9630.00")]

    pay(client, h["accountant"], invoice, "630.00")
    partial = client.get("/api/accounting/receivables", headers=h["accountant"]).json()
    assert partial["total_open"] == "9000.00"

    pay(client, h["accountant"], invoice, "9000.00")
    after = client.get("/api/accounting/receivables", headers=h["accountant"]).json()
    assert after == {"items": [], "total_open": "0.00"}
