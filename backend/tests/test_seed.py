from siam_bean_erp.seed import DEMO_PASSWORD, seed


def test_seeding_creates_demo_accounts_covering_every_role_and_can_be_repeated(client, conn):
    seed(conn)
    seed(conn)

    roles = conn.execute(
        "select role from profiles where email like %s order by role", ("%@siambean.test",)
    ).fetchall()
    assert [r["role"] for r in roles] == ["accountant", "admin", "sales", "sales", "warehouse"]


def test_a_seeded_demo_account_can_log_in(client, conn):
    seed(conn)

    response = client.post(
        "/api/auth/login", json={"email": "nok@siambean.test", "password": DEMO_PASSWORD}
    )

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "sales"


def test_seeding_loads_the_four_sample_products_from_the_scenario(conn):
    seed(conn)
    seed(conn)

    rows = conn.execute(
        "select sku, name, unit, cost, price, reorder_level from products order by sku"
    ).fetchall()
    by_sku = {r["sku"]: r for r in rows}
    assert set(by_sku) == {"ARB-1KG", "ROB-1KG", "BLD-1KG", "DRP-10"}
    arabica = by_sku["ARB-1KG"]
    assert (arabica["name"], arabica["unit"], int(arabica["cost"]), int(arabica["price"])) == (
        "Arabica, 1 kg bag", "kg", 320, 450,
    )
    assert by_sku["DRP-10"]["reorder_level"] == 100


def test_seeding_loads_the_three_sample_customers_once(conn):
    seed(conn)
    seed(conn)

    rows = conn.execute("select name, tax_id, payment_terms from customers order by name").fetchall()
    assert [(r["name"], r["tax_id"], r["payment_terms"]) for r in rows] == [
        ("Brew Lab Ari", "0105562000022", "Cash"),
        ("Café Lune", "0105561000011", "30 days"),
        ("Sukhumvit Corner Café", "0105563000033", "15 days"),
    ]
