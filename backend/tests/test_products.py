import pytest

ARABICA = {
    "sku": "ARB-1KG",
    "name": "Arabica, 1 kg bag",
    "unit": "kg",
    "cost": "320",
    "price": "450",
    "reorder_level": 50,
}


def create(client, headers, **changes):
    return client.post("/api/products", json={**ARABICA, **changes}, headers=headers)


def test_an_admin_creates_a_product_and_money_comes_back_as_exact_text(client, auth):
    response = create(client, auth("admin"))

    assert response.status_code == 201
    body = response.json()
    assert (body["sku"], body["price"], body["cost"], body["active"]) == ("ARB-1KG", "450.00", "320.00", True)


def test_a_duplicate_sku_is_rejected(client, auth):
    admin = auth("admin")
    create(client, admin)

    response = create(client, admin)

    assert response.status_code == 409
    assert response.json()["detail"] == "SKU already exists"


@pytest.mark.parametrize(
    "changes,message",
    [
        ({"sku": "arb 1kg"}, "SKU can only use capital letters, digits and hyphens"),
        ({"sku": "arb-1kg"}, "SKU can only use capital letters, digits and hyphens"),
        ({"sku": ""}, "SKU is required"),
        ({"name": " "}, "Name is required"),
        ({"unit": ""}, "Unit is required"),
        ({"price": "-1"}, "Price cannot be below 0"),
        ({"cost": "-0.01"}, "Cost cannot be below 0"),
        ({"price": "abc"}, "Price must be a number"),
        ({"price": "10.555"}, "Price can have at most 2 decimals"),
        ({"reorder_level": -1}, "Reorder level cannot be below 0"),
    ],
)
def test_bad_product_input_says_what_to_fix(client, auth, changes, message):
    response = create(client, auth("admin"), **changes)

    assert response.status_code == 422
    assert response.json()["detail"] == message


def test_an_admin_edits_name_price_cost_and_reorder_level(client, auth):
    admin = auth("admin")
    product = create(client, admin).json()

    response = client.patch(
        f"/api/products/{product['id']}",
        json={"name": "Arabica 1 kg", "price": "480", "cost": "330", "reorder_level": 60},
        headers=admin,
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["name"], body["price"], body["cost"], body["reorder_level"]) == ("Arabica 1 kg", "480.00", "330.00", 60)


def test_a_sku_cannot_be_changed_after_creation(client, auth):
    admin = auth("admin")
    product = create(client, admin).json()

    response = client.patch(f"/api/products/{product['id']}", json={"sku": "NEW-1KG"}, headers=admin)

    assert response.status_code == 422
    assert response.json()["detail"] == "SKU cannot be changed"


def test_deactivating_hides_a_product_from_active_lists_and_keeps_its_sku_reserved(client, auth):
    admin = auth("admin")
    product = create(client, admin).json()

    client.patch(f"/api/products/{product['id']}", json={"active": False}, headers=admin)

    active_skus = [p["sku"] for p in client.get("/api/products?active=true", headers=admin).json()]
    all_skus = [p["sku"] for p in client.get("/api/products", headers=admin).json()]
    assert "ARB-1KG" not in active_skus
    assert "ARB-1KG" in all_skus
    assert create(client, admin).status_code == 409


def test_an_admin_reactivates_a_product(client, auth):
    admin = auth("admin")
    product = create(client, admin).json()
    client.patch(f"/api/products/{product['id']}", json={"active": False}, headers=admin)

    response = client.patch(f"/api/products/{product['id']}", json={"active": True}, headers=admin)

    assert response.json()["active"] is True


@pytest.mark.parametrize("role", ["sales", "warehouse", "accountant"])
def test_other_roles_can_list_products_but_not_change_them(client, auth, role):
    admin = auth("admin")
    product = create(client, admin).json()
    headers = auth(role)

    assert client.get("/api/products", headers=headers).status_code == 200
    assert client.get(f"/api/products/{product['id']}", headers=headers).status_code == 200
    assert create(client, headers, sku="OTHER-1").status_code == 403
    assert client.patch(f"/api/products/{product['id']}", json={"price": "1"}, headers=headers).status_code == 403


def test_products_require_a_login(client):
    assert client.get("/api/products").status_code == 401


def test_a_missing_product_is_a_404(client, auth):
    response = client.get("/api/products/00000000-0000-0000-0000-000000000000", headers=auth("admin"))

    assert response.status_code == 404
