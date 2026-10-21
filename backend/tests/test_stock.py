import pytest

from siam_bean_erp.seed import seed


@pytest.fixture
def arabica(client, auth):
    response = client.post(
        "/api/products",
        json={"sku": "ARB-1KG", "name": "Arabica", "unit": "kg", "cost": "320", "price": "450", "reorder_level": 50},
        headers=auth("admin"),
    )
    return response.json()


def stock_in(client, headers, product, quantity, note="delivery"):
    return client.post(
        "/api/stock/in", json={"product_id": product["id"], "quantity": quantity, "note": note}, headers=headers
    )


def adjust(client, headers, product, quantity, reason="recount"):
    body = {"product_id": product["id"], "quantity": quantity}
    if reason is not None:
        body["reason"] = reason
    return client.post("/api/stock/adjustments", json=body, headers=headers)


def on_hand(client, headers, product):
    return client.get(f"/api/products/{product['id']}", headers=headers).json()["on_hand"]


# ---- 06 stock in and On Hand -------------------------------------------------------------


def test_a_new_product_has_nothing_on_hand(client, auth, arabica):
    assert on_hand(client, auth("sales"), arabica) == 0


def test_stock_in_raises_on_hand_by_exactly_that_quantity(client, auth, arabica):
    warehouse = auth("warehouse")

    response = stock_in(client, warehouse, arabica, 170)

    assert response.status_code == 201
    assert on_hand(client, warehouse, arabica) == 170
    stock_in(client, warehouse, arabica, 5)
    assert on_hand(client, warehouse, arabica) == 175


@pytest.mark.parametrize("quantity", [0, -5])
def test_stock_in_needs_a_quantity_above_zero(client, auth, arabica, quantity):
    response = stock_in(client, auth("warehouse"), arabica, quantity)

    assert response.status_code == 422
    assert response.json()["detail"] == "Quantity must be above 0"


def test_stock_in_for_an_unknown_product_says_so(client, auth):
    response = client.post(
        "/api/stock/in",
        json={"product_id": "00000000-0000-0000-0000-000000000000", "quantity": 5},
        headers=auth("warehouse"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_nobody_can_type_an_on_hand_number(client, auth, arabica):
    admin = auth("admin")
    stock_in(client, admin, arabica, 10)

    client.patch(f"/api/products/{arabica['id']}", json={"on_hand": 999}, headers=admin)

    assert on_hand(client, admin, arabica) == 10
    assert client.put(f"/api/products/{arabica['id']}", json={"on_hand": 999}, headers=admin).status_code == 405


def test_the_movement_history_lists_type_quantity_reason_user_and_time(client, auth, arabica, make_user):
    from siam_bean_erp.security import create_token

    lek = make_user("warehouse")
    headers = {"Authorization": f"Bearer {create_token(lek['id'])}"}
    stock_in(client, headers, arabica, 170, note="opening count")

    history = client.get(f"/api/stock/movements?product_id={arabica['id']}", headers=headers).json()

    assert len(history) == 1
    row = history[0]
    assert (row["movement_type"], row["quantity"], row["reason"], row["user_name"], row["sku"]) == (
        "stock_in", 170, "opening count", lek["full_name"], "ARB-1KG",
    )
    assert row["created_at"]


def test_history_is_newest_first(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 10, note="first")
    stock_in(client, warehouse, arabica, 20, note="second")

    history = client.get(f"/api/stock/movements?product_id={arabica['id']}", headers=warehouse).json()

    assert [h["reason"] for h in history] == ["second", "first"]


@pytest.mark.parametrize("role,expected", [("admin", 201), ("warehouse", 201), ("sales", 403), ("accountant", 403)])
def test_who_can_record_stock_in(client, auth, arabica, role, expected):
    assert stock_in(client, auth(role), arabica, 5).status_code == expected


@pytest.mark.parametrize("role,expected", [("admin", 200), ("warehouse", 200), ("sales", 403), ("accountant", 403)])
def test_who_can_read_movement_history(client, auth, arabica, role, expected):
    assert client.get("/api/stock/movements", headers=auth(role)).status_code == expected


@pytest.mark.parametrize("role", ["sales", "warehouse", "accountant", "admin"])
def test_every_role_that_views_products_sees_on_hand(client, auth, arabica, role):
    stock_in(client, auth("warehouse"), arabica, 7)

    listed = client.get("/api/products", headers=auth(role)).json()

    assert [p["on_hand"] for p in listed if p["sku"] == "ARB-1KG"] == [7]


def test_seeding_loads_the_opening_stock_once(client, conn, auth):
    seed(conn)
    seed(conn)

    listed = {p["sku"]: p["on_hand"] for p in client.get("/api/products", headers=auth("sales")).json()}

    assert listed["ARB-1KG"] == 170
    assert listed["ROB-1KG"] == 35
    assert listed["BLD-1KG"] == 90
    assert listed["DRP-10"] == 240


# ---- 07 adjustments ---------------------------------------------------------------------


def test_an_adjustment_can_add_or_remove_stock_with_a_reason(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 100)

    assert adjust(client, warehouse, arabica, -8, "damaged bags").status_code == 201
    assert on_hand(client, warehouse, arabica) == 92
    assert adjust(client, warehouse, arabica, 3, "recount").status_code == 201
    assert on_hand(client, warehouse, arabica) == 95


def test_an_adjustment_without_a_reason_is_rejected(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 100)

    missing = adjust(client, warehouse, arabica, -1, reason=None)
    blank = adjust(client, warehouse, arabica, -1, reason="  ")

    assert missing.status_code == blank.status_code == 422
    assert missing.json()["detail"] == blank.json()["detail"] == "Reason is required"
    assert on_hand(client, warehouse, arabica) == 100


def test_an_adjustment_of_zero_is_rejected(client, auth, arabica):
    response = adjust(client, auth("warehouse"), arabica, 0)

    assert response.status_code == 422
    assert response.json()["detail"] == "Quantity cannot be 0"


def test_an_adjustment_that_would_go_below_zero_is_rejected_and_changes_nothing(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 10)

    response = adjust(client, warehouse, arabica, -11, "lost")

    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough stock for ARB-1KG"
    assert on_hand(client, warehouse, arabica) == 10
    history = client.get(f"/api/stock/movements?product_id={arabica['id']}", headers=warehouse).json()
    assert len(history) == 1


def test_the_adjustment_shows_in_history_with_its_reason_and_user(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 10)
    adjust(client, warehouse, arabica, -2, "samples for a cafe")

    history = client.get(f"/api/stock/movements?product_id={arabica['id']}", headers=warehouse).json()

    assert (history[0]["movement_type"], history[0]["quantity"], history[0]["reason"]) == (
        "adjustment", -2, "samples for a cafe",
    )


@pytest.mark.parametrize("role,expected", [("admin", 201), ("warehouse", 201), ("sales", 403), ("accountant", 403)])
def test_who_can_adjust_stock(client, auth, arabica, role, expected):
    stock_in(client, auth("warehouse"), arabica, 10)

    assert adjust(client, auth(role), arabica, 1).status_code == expected


# ---- 08 Low Stock -----------------------------------------------------------------------


def low_stock_flags(client, headers):
    return {p["sku"]: p["low_stock"] for p in client.get("/api/products", headers=headers).json()}


def test_a_product_below_its_reorder_level_is_flagged_low_stock(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 49)

    assert low_stock_flags(client, warehouse)["ARB-1KG"] is True


def test_a_product_exactly_at_its_reorder_level_is_not_low_stock(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 50)

    assert low_stock_flags(client, warehouse)["ARB-1KG"] is False


def test_stock_in_lifts_a_product_out_of_low_stock(client, auth, arabica):
    warehouse = auth("warehouse")
    stock_in(client, warehouse, arabica, 10)
    assert low_stock_flags(client, warehouse)["ARB-1KG"] is True

    stock_in(client, warehouse, arabica, 40)

    assert low_stock_flags(client, warehouse)["ARB-1KG"] is False


def test_in_the_sample_data_only_robusta_starts_low(client, conn, auth):
    seed(conn)

    flags = low_stock_flags(client, auth("warehouse"))

    assert (flags["ARB-1KG"], flags["ROB-1KG"], flags["BLD-1KG"], flags["DRP-10"]) == (False, True, False, False)
