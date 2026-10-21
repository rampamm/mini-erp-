import time

import pytest

LUNE = {"name": "Café Lune", "tax_id": "0105561000011", "payment_terms": "30 days"}


def create(client, headers, **changes):
    return client.post("/api/customers", json={**LUNE, **changes}, headers=headers)


def test_sales_creates_a_customer(client, auth):
    response = create(client, auth("sales"))

    assert response.status_code == 201
    body = response.json()
    assert (body["name"], body["tax_id"], body["payment_terms"], body["active"]) == (
        "Café Lune", "0105561000011", "30 days", True,
    )


@pytest.mark.parametrize(
    "changes,message",
    [
        ({"tax_id": "123"}, "Tax ID must be 13 digits"),
        ({"tax_id": "01055610000AB"}, "Tax ID must be 13 digits"),
        ({"tax_id": "01055610000111"}, "Tax ID must be 13 digits"),
        ({"tax_id": ""}, "Tax ID is required"),
        ({"name": "  "}, "Name is required"),
        ({"payment_terms": "60 days"}, "Payment terms must be one of: Cash, 15 days, 30 days"),
    ],
)
def test_bad_customer_input_says_what_to_fix(client, auth, changes, message):
    response = create(client, auth("sales"), **changes)

    assert response.status_code == 422
    assert response.json()["detail"] == message


def test_a_missing_tax_id_is_required(client, auth):
    body = {k: v for k, v in LUNE.items() if k != "tax_id"}

    response = client.post("/api/customers", json=body, headers=auth("sales"))

    assert response.status_code == 422
    assert response.json()["detail"] == "Tax ID is required"


def test_sales_edits_a_customer(client, auth):
    sales = auth("sales")
    customer = create(client, sales).json()

    response = client.patch(
        f"/api/customers/{customer['id']}",
        json={"name": "Café Lune Ari", "payment_terms": "15 days"},
        headers=sales,
    )

    assert response.status_code == 200
    assert (response.json()["name"], response.json()["payment_terms"]) == ("Café Lune Ari", "15 days")


def test_sales_deactivates_but_only_an_admin_reactivates(client, auth):
    sales, admin = auth("sales"), auth("admin")
    customer = create(client, sales).json()

    deactivated = client.patch(f"/api/customers/{customer['id']}", json={"active": False}, headers=sales)
    assert deactivated.json()["active"] is False

    refused = client.patch(f"/api/customers/{customer['id']}", json={"active": True}, headers=sales)
    assert refused.status_code == 403
    assert refused.json()["detail"] == "Only an Admin can reactivate a customer"

    reactivated = client.patch(f"/api/customers/{customer['id']}", json={"active": True}, headers=admin)
    assert reactivated.json()["active"] is True


def test_active_filter_hides_deactivated_customers(client, auth):
    sales = auth("sales")
    customer = create(client, sales).json()
    client.patch(f"/api/customers/{customer['id']}", json={"active": False}, headers=sales)

    names = [c["name"] for c in client.get("/api/customers?active=true", headers=sales).json()["items"]]

    assert "Café Lune" not in names


@pytest.fixture
def two_hundred_customers(conn):
    conn.execute(
        "insert into customers (name, tax_id, payment_terms)"
        " select 'Café ' || lpad(g::text, 3, '0'), lpad(g::text, 13, '0'), 'Cash' from generate_series(1, 200) g"
    )
    conn.execute(
        "insert into customers (name, tax_id, payment_terms) values ('Brew Lab Ari', '0105562000022', 'Cash')"
    )


def test_search_matches_part_of_a_name_ignoring_case(client, auth, two_hundred_customers):
    response = client.get("/api/customers?q=brew LAB", headers=auth("sales"))

    body = response.json()
    assert [c["name"] for c in body["items"]] == ["Brew Lab Ari"]
    assert body["total"] == 1


def test_search_returns_at_most_20_rows_per_page_sorted_by_name_and_is_fast(client, auth, two_hundred_customers):
    sales = auth("sales")

    started = time.perf_counter()
    first = client.get("/api/customers?q=café", headers=sales).json()
    elapsed = time.perf_counter() - started

    assert elapsed < 1
    assert first["total"] == 200
    assert len(first["items"]) == 20
    assert first["page"] == 1 and first["page_size"] == 20
    names = [c["name"] for c in first["items"]]
    assert names == sorted(names) and names[0] == "Café 001"
    second = client.get("/api/customers?q=café&page=2", headers=sales).json()
    assert second["items"][0]["name"] == "Café 021"


def test_a_search_with_percent_or_underscore_is_taken_literally(client, auth, two_hundred_customers):
    assert client.get("/api/customers?q=%25", headers=auth("sales")).json()["total"] == 0
    assert client.get("/api/customers?q=_", headers=auth("sales")).json()["total"] == 0


def test_a_search_with_no_match_returns_an_empty_page(client, auth, two_hundred_customers):
    body = client.get("/api/customers?q=zzzz", headers=auth("sales")).json()

    assert body["items"] == [] and body["total"] == 0


@pytest.mark.parametrize("role,list_status,write_status", [
    ("admin", 200, 201),
    ("sales", 200, 201),
    ("accountant", 200, 403),
    ("warehouse", 403, 403),
])
def test_customer_access_by_role(client, auth, role, list_status, write_status):
    headers = auth(role)

    assert client.get("/api/customers", headers=headers).status_code == list_status
    assert create(client, headers).status_code == write_status


def test_a_missing_customer_is_a_404(client, auth):
    response = client.patch(
        "/api/customers/00000000-0000-0000-0000-000000000000", json={"name": "X"}, headers=auth("sales")
    )

    assert response.status_code == 404
