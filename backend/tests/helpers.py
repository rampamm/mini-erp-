"""Small builders that drive the API the way a user would."""


def make_product(client, headers, sku="ARB-1KG", price="450", cost="320", reorder_level=50, unit="kg", name=None):
    response = client.post(
        "/api/products",
        json={
            "sku": sku,
            "name": name or f"Product {sku}",
            "unit": unit,
            "cost": cost,
            "price": price,
            "reorder_level": reorder_level,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def make_customer(client, headers, name="Café Lune", payment_terms="30 days", tax_id="0105561000011"):
    response = client.post(
        "/api/customers",
        json={"name": name, "tax_id": tax_id, "payment_terms": payment_terms},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def put_stock(client, headers, product, quantity):
    response = client.post(
        "/api/stock/in", json={"product_id": product["id"], "quantity": quantity, "note": "test"}, headers=headers
    )
    assert response.status_code == 201, response.text


def order_body(customer, lines):
    return {
        "customer_id": customer["id"],
        "lines": [{"product_id": product["id"], "quantity": quantity} for product, quantity in lines],
    }


def make_order(client, headers, customer, lines):
    response = client.post("/api/orders", json=order_body(customer, lines), headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def confirm(client, headers, order):
    return client.post(f"/api/orders/{order['id']}/confirm", headers=headers)
