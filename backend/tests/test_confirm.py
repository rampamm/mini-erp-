import threading

import psycopg
import pytest
from fastapi.testclient import TestClient
from helpers import confirm, make_customer, make_order, make_product, put_stock
from psycopg.rows import dict_row

from siam_bean_erp.app import create_app
from siam_bean_erp.db import get_conn
from siam_bean_erp.security import create_token


@pytest.fixture
def shop(client, h):
    arabica = make_product(client, h["admin"], "ARB-1KG", price="450")
    robusta = make_product(client, h["admin"], "ROB-1KG", price="320", reorder_level=40)
    put_stock(client, h["warehouse"], arabica, 170)
    put_stock(client, h["warehouse"], robusta, 35)
    lune = make_customer(client, h["sales"], "Café Lune")
    return {"arabica": arabica, "robusta": robusta, "lune": lune}


def on_hand(client, headers, product):
    return client.get(f"/api/products/{product['id']}", headers=headers).json()["on_hand"]


# ---- 10 confirm order issues invoice ---------------------------------------------------


def test_confirming_the_cafe_lune_order_deducts_stock_and_issues_the_invoice(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)])

    response = confirm(client, h["sales"], order)

    assert response.status_code == 200
    body = response.json()
    assert (body["status"], body["number"], body["invoice_number"]) == ("confirmed", "SO-0001", "INV-0001")
    assert (body["subtotal"], body["vat"], body["total"]) == ("9000.00", "630.00", "9630.00")
    assert body["confirmed_at"] is not None
    assert on_hand(client, h["sales"], shop["arabica"]) == 150


def test_document_numbers_are_sequential(client, h, shop):
    first = confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])).json()
    second = confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])).json()

    assert (first["number"], first["invoice_number"]) == ("SO-0001", "INV-0001")
    assert (second["number"], second["invoice_number"]) == ("SO-0002", "INV-0002")


def test_vat_is_rounded_half_up_to_two_decimals(client, h, shop):
    cheap = make_product(client, h["admin"], "CHEAP-1", price="1.50", cost="1")
    put_stock(client, h["warehouse"], cheap, 5)

    body = confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], [(cheap, 1)])).json()

    assert (body["subtotal"], body["vat"], body["total"]) == ("1.50", "0.11", "1.61")


def test_the_sale_shows_in_the_stock_history_with_the_order_number(client, h, shop):
    confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)]))

    history = client.get(f"/api/stock/movements?product_id={shop['arabica']['id']}", headers=h["warehouse"]).json()

    assert (history[0]["movement_type"], history[0]["quantity"], history[0]["reason"]) == ("sale", -20, "SO-0001")


def test_a_confirmed_order_is_read_only(client, h, shop):
    order = confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 2)])).json()
    body = {"customer_id": shop["lune"]["id"], "lines": []}

    changed = client.put(f"/api/orders/{order['id']}", json=body, headers=h["sales"])
    deleted = client.delete(f"/api/orders/{order['id']}", headers=h["sales"])

    assert (changed.status_code, deleted.status_code) == (409, 409)
    assert changed.json()["detail"] == "A confirmed order cannot be changed"
    still = client.get(f"/api/orders/{order['id']}", headers=h["sales"]).json()
    assert len(still["lines"]) == 1


def test_confirming_twice_is_refused_and_deducts_stock_only_once(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)])
    confirm(client, h["sales"], order)

    again = confirm(client, h["sales"], order)

    assert again.status_code == 409
    assert again.json()["detail"] == "This order is already confirmed"
    assert on_hand(client, h["sales"], shop["arabica"]) == 150


def test_confirming_an_unknown_order_is_a_404(client, h):
    response = client.post("/api/orders/00000000-0000-0000-0000-000000000000/confirm", headers=h["sales"])

    assert response.status_code == 404


@pytest.mark.parametrize("role,expected", [("admin", 200), ("sales", 200), ("warehouse", 403), ("accountant", 403)])
def test_who_can_confirm(client, h, shop, role, expected):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])

    assert confirm(client, h[role], order).status_code == expected
    if expected == 403:
        assert on_hand(client, h["sales"], shop["arabica"]) == 170


# ---- 11 not enough stock, all-or-nothing, racing confirms ---------------------------------


def test_too_little_stock_fails_with_the_sku_and_changes_nothing(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 171)])

    response = confirm(client, h["sales"], order)

    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough stock for ARB-1KG"
    assert on_hand(client, h["sales"], shop["arabica"]) == 170
    after = client.get(f"/api/orders/{order['id']}", headers=h["sales"]).json()
    assert (after["status"], after["number"], after["invoice_id"]) == ("draft", None, None)


def test_a_failed_confirm_leaves_no_gap_in_the_numbers(client, h, shop):
    too_big = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 999)])
    assert confirm(client, h["sales"], too_big).status_code == 409

    fine = confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])).json()

    assert (fine["number"], fine["invoice_number"]) == ("SO-0001", "INV-0001")


def test_if_one_line_is_short_no_line_is_deducted(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20), (shop["robusta"], 36)])

    response = confirm(client, h["sales"], order)

    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough stock for ROB-1KG"
    assert on_hand(client, h["sales"], shop["arabica"]) == 170
    assert on_hand(client, h["sales"], shop["robusta"]) == 35


def test_an_order_with_no_lines_cannot_be_confirmed(client, h, shop):
    response = confirm(client, h["sales"], make_order(client, h["sales"], shop["lune"], []))

    assert response.status_code == 409
    assert response.json()["detail"] == "Add at least one line before confirming"


def test_a_product_deactivated_after_the_draft_blocks_the_confirm(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])
    client.patch(f"/api/products/{shop['arabica']['id']}", json={"active": False}, headers=h["admin"])

    response = confirm(client, h["sales"], order)

    assert response.status_code == 409
    assert response.json()["detail"] == "Product ARB-1KG is deactivated"
    assert on_hand(client, h["sales"], shop["arabica"]) == 170


def test_a_customer_deactivated_after_the_draft_blocks_the_confirm(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])
    client.patch(f"/api/customers/{shop['lune']['id']}", json={"active": False}, headers=h["sales"])

    response = confirm(client, h["sales"], order)

    assert response.status_code == 409
    assert response.json()["detail"] == "Customer Café Lune is deactivated"


def test_two_confirms_racing_for_the_same_stock_never_oversell(test_db_url):
    """Real committed data and two real connections: only one of the two orders can win."""
    tables = (
        "payments, invoice_lines, invoices, sales_order_lines, sales_orders, stock_movements,"
        " customers, products, profiles"
    )

    def wipe(setup):
        setup.execute(f"truncate {tables} restart identity cascade")
        setup.execute("update document_counters set last_value = 0")

    def open_client():
        connection = psycopg.connect(test_db_url, autocommit=True, row_factory=dict_row)
        app = create_app()
        app.dependency_overrides[get_conn] = lambda: connection
        return connection, TestClient(app)

    setup, api = open_client()
    wipe(setup)
    try:
        def headers_for(role):
            user = setup.execute(
                "insert into profiles (email, full_name, role) values (%s, %s, %s) returning id",
                (f"{role}@race.test", role, role),
            ).fetchone()
            return {"Authorization": f"Bearer {create_token(user['id'])}"}

        admin, warehouse, sales = headers_for("admin"), headers_for("warehouse"), headers_for("sales")
        coffee = make_product(api, admin, "ARB-1KG", price="450")
        put_stock(api, warehouse, coffee, 20)
        customer = make_customer(api, sales, "Café Lune")
        first = make_order(api, sales, customer, [(coffee, 15)])
        second = make_order(api, sales, customer, [(coffee, 15)])

        results = {}
        barrier = threading.Barrier(2)

        def attempt(name, order):
            connection, client = open_client()
            try:
                barrier.wait()
                results[name] = confirm(client, sales, order)
            finally:
                connection.close()

        threads = [
            threading.Thread(target=attempt, args=("first", first)),
            threading.Thread(target=attempt, args=("second", second)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)

        assert sorted(r.status_code for r in results.values()) == [200, 409]
        loser = next(r for r in results.values() if r.status_code == 409)
        assert loser.json()["detail"] == "Not enough stock for ARB-1KG"
        assert on_hand(api, sales, coffee) == 5
        assert setup.execute("select count(*) as n from invoices").fetchone()["n"] == 1
    finally:
        wipe(setup)
        setup.close()
