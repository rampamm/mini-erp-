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
