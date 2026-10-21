import pytest
from helpers import make_customer, make_order, make_product, order_body, put_stock

ZERO_UUID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def shop(client, h):
    admin, warehouse = h["admin"], h["warehouse"]
    arabica = make_product(client, admin, "ARB-1KG", price="450")
    robusta = make_product(client, admin, "ROB-1KG", price="320", reorder_level=40)
    put_stock(client, warehouse, arabica, 170)
    put_stock(client, warehouse, robusta, 35)
    lune = make_customer(client, h["sales"], "Café Lune")
    return {"arabica": arabica, "robusta": robusta, "lune": lune}


def test_sales_creates_a_draft_with_prices_copied_and_totals_calculated(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20), (shop["robusta"], 5)])

    assert order["status"] == "draft"
    assert order["number"] is None
    assert order["customer"]["name"] == "Café Lune"
    lines = {line["sku"]: line for line in order["lines"]}
    assert (lines["ARB-1KG"]["unit_price"], lines["ARB-1KG"]["quantity"], lines["ARB-1KG"]["line_total"]) == (
        "450.00", 20, "9000.00",
    )
    assert lines["ROB-1KG"]["line_total"] == "1600.00"
    assert (order["subtotal"], order["vat"], order["total"]) == ("10600.00", "742.00", "11342.00")


def test_a_draft_does_not_touch_stock(client, h, shop):
    make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)])

    product = client.get(f"/api/products/{shop['arabica']['id']}", headers=h["sales"]).json()
    assert product["on_hand"] == 170


def test_each_line_shows_the_current_on_hand(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)])

    assert order["lines"][0]["on_hand"] == 170


def test_a_line_price_sent_by_the_client_is_ignored(client, h, shop):
    body = order_body(shop["lune"], [(shop["arabica"], 2)])
    body["lines"][0]["unit_price"] = "1.00"

    response = client.post("/api/orders", json=body, headers=h["sales"])

    assert response.json()["lines"][0]["unit_price"] == "450.00"


def test_a_later_price_change_does_not_change_lines_already_on_a_draft(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)])
    client.patch(f"/api/products/{shop['arabica']['id']}", json={"price": "500"}, headers=h["admin"])

    reloaded = client.get(f"/api/orders/{order['id']}", headers=h["sales"]).json()
    assert reloaded["lines"][0]["unit_price"] == "450.00"

    resaved = client.put(
        f"/api/orders/{order['id']}",
        json=order_body(shop["lune"], [(shop["arabica"], 25), (shop["robusta"], 1)]),
        headers=h["sales"],
    ).json()
    prices = {line["sku"]: line["unit_price"] for line in resaved["lines"]}
    assert prices == {"ARB-1KG": "450.00", "ROB-1KG": "320.00"}


def test_the_same_product_twice_is_merged_into_one_line(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 5), (shop["arabica"], 7)])

    assert [(line["sku"], line["quantity"]) for line in order["lines"]] == [("ARB-1KG", 12)]


@pytest.mark.parametrize("quantity", [0, -3])
def test_a_quantity_must_be_above_zero(client, h, shop, quantity):
    body = order_body(shop["lune"], [(shop["arabica"], quantity)])

    response = client.post("/api/orders", json=body, headers=h["sales"])

    assert response.status_code == 422
    assert response.json()["detail"] == "Quantity must be above 0"


def test_a_draft_can_be_saved_with_no_lines_yet(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [])

    assert order["lines"] == [] and order["total"] == "0.00"


def test_a_missing_customer_is_required(client, h, shop):
    response = client.post("/api/orders", json={"lines": []}, headers=h["sales"])

    assert response.status_code == 422
    assert response.json()["detail"] == "Customer is required"


def test_unknown_customers_and_products_are_reported(client, h, shop):
    unknown_customer = client.post("/api/orders", json={"customer_id": ZERO_UUID, "lines": []}, headers=h["sales"])
    unknown_product = client.post(
        "/api/orders",
        json={"customer_id": shop["lune"]["id"], "lines": [{"product_id": ZERO_UUID, "quantity": 1}]},
        headers=h["sales"],
    )

    assert (unknown_customer.status_code, unknown_customer.json()["detail"]) == (404, "Customer not found")
    assert (unknown_product.status_code, unknown_product.json()["detail"]) == (404, "Product not found")


def test_deactivated_products_and_customers_cannot_be_put_on_a_draft(client, h, shop):
    client.patch(f"/api/products/{shop['robusta']['id']}", json={"active": False}, headers=h["admin"])
    product_response = client.post(
        "/api/orders", json=order_body(shop["lune"], [(shop["robusta"], 1)]), headers=h["sales"]
    )
    assert product_response.status_code == 409
    assert product_response.json()["detail"] == "Product ROB-1KG is deactivated"

    client.patch(f"/api/customers/{shop['lune']['id']}", json={"active": False}, headers=h["sales"])
    customer_response = client.post("/api/orders", json=order_body(shop["lune"], []), headers=h["sales"])
    assert customer_response.status_code == 409
    assert customer_response.json()["detail"] == "Customer Café Lune is deactivated"


def test_sales_edits_a_draft_by_replacing_its_customer_and_lines(client, h, shop):
    other = make_customer(client, h["sales"], "Brew Lab Ari", "Cash", "0105562000022")
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)])

    updated = client.put(
        f"/api/orders/{order['id']}", json=order_body(other, [(shop["robusta"], 3)]), headers=h["sales"]
    )

    assert updated.status_code == 200
    body = updated.json()
    assert body["customer"]["name"] == "Brew Lab Ari"
    assert [(line["sku"], line["quantity"]) for line in body["lines"]] == [("ROB-1KG", 3)]


def test_sales_deletes_a_draft(client, h, shop):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 20)])

    assert client.delete(f"/api/orders/{order['id']}", headers=h["sales"]).status_code == 204
    assert client.get(f"/api/orders/{order['id']}", headers=h["sales"]).status_code == 404


def test_the_order_list_can_be_filtered_by_status(client, h, shop):
    make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])

    drafts = client.get("/api/orders?status=draft", headers=h["sales"]).json()
    confirmed = client.get("/api/orders?status=confirmed", headers=h["sales"]).json()

    assert [(o["status"], o["customer_name"], o["total"]) for o in drafts] == [("draft", "Café Lune", "481.50")]
    assert confirmed == []


@pytest.mark.parametrize("role,expected", [("admin", 201), ("sales", 201), ("warehouse", 403), ("accountant", 403)])
def test_who_can_prepare_orders(client, h, shop, role, expected):
    response = client.post("/api/orders", json=order_body(shop["lune"], []), headers=h[role])

    assert response.status_code == expected


@pytest.mark.parametrize("role", ["warehouse", "accountant"])
def test_warehouse_and_accountant_cannot_read_or_change_orders(client, h, shop, role):
    order = make_order(client, h["sales"], shop["lune"], [(shop["arabica"], 1)])
    headers = h[role]

    assert client.get("/api/orders", headers=headers).status_code == 403
    assert client.get(f"/api/orders/{order['id']}", headers=headers).status_code == 403
    assert client.put(f"/api/orders/{order['id']}", json=order_body(shop["lune"], []), headers=headers).status_code == 403
    assert client.delete(f"/api/orders/{order['id']}", headers=headers).status_code == 403
