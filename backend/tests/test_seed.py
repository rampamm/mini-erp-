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
