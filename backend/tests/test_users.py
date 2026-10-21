import pytest

NEW_USER = {"email": "mali@test.local", "full_name": "Mali", "role": "warehouse", "password": "temp-pass-1"}


def test_an_admin_creates_a_user_who_can_then_log_in(client, auth):
    created = client.post("/api/users", json=NEW_USER, headers=auth("admin"))

    assert created.status_code == 201
    assert created.json()["role"] == "warehouse"
    assert "password" not in created.json() and "password_hash" not in created.json()
    login = client.post("/api/auth/login", json={"email": "mali@test.local", "password": "temp-pass-1"})
    assert login.status_code == 200


def test_there_is_no_public_sign_up(client):
    assert client.post("/api/auth/signup", json=NEW_USER).status_code in (404, 405)
    assert client.post("/api/users", json=NEW_USER).status_code == 401


def test_an_admin_changes_a_role_and_it_applies_on_the_next_request(client, auth, make_user):
    admin = auth("admin")
    user = make_user("sales")
    from siam_bean_erp.security import create_token

    token = {"Authorization": f"Bearer {create_token(user['id'])}"}
    assert client.get("/api/users", headers=token).status_code == 403

    changed = client.patch(f"/api/users/{user['id']}", json={"role": "admin"}, headers=admin)

    assert changed.status_code == 200
    assert client.get("/api/users", headers=token).status_code == 200


def test_an_admin_deactivates_and_reactivates_a_user(client, auth, make_user):
    admin = auth("admin")
    user = make_user("sales")
    from siam_bean_erp.security import create_token

    token = {"Authorization": f"Bearer {create_token(user['id'])}"}

    client.patch(f"/api/users/{user['id']}", json={"active": False}, headers=admin)
    assert client.get("/api/auth/me", headers=token).status_code == 401

    client.patch(f"/api/users/{user['id']}", json={"active": True}, headers=admin)
    assert client.get("/api/auth/me", headers=token).status_code == 200


@pytest.mark.parametrize("role", ["sales", "warehouse", "accountant"])
def test_other_roles_cannot_manage_users(client, auth, make_user, role):
    headers = auth(role)
    target = make_user("sales")

    assert client.post("/api/users", json=NEW_USER, headers=headers).status_code == 403
    assert client.patch(f"/api/users/{target['id']}", json={"active": False}, headers=headers).status_code == 403


@pytest.mark.parametrize(
    "change,message",
    [
        ({"email": ""}, "Enter a valid email address"),
        ({"email": "not-an-email"}, "Enter a valid email address"),
        ({"full_name": "  "}, "Name is required"),
        ({"role": "boss"}, "Role must be one of: admin, sales, warehouse, accountant"),
        ({"password": "short"}, "Password must be at least 8 characters"),
    ],
)
def test_bad_input_is_rejected_with_a_message_saying_what_to_fix(client, auth, change, message):
    response = client.post("/api/users", json={**NEW_USER, **change}, headers=auth("admin"))

    assert response.status_code == 422
    assert response.json()["detail"] == message


def test_a_missing_field_is_named(client, auth):
    body = {k: v for k, v in NEW_USER.items() if k != "email"}

    response = client.post("/api/users", json=body, headers=auth("admin"))

    assert response.status_code == 422
    assert response.json()["detail"] == "Email is required"


def test_a_duplicate_email_is_rejected(client, auth):
    admin = auth("admin")
    client.post("/api/users", json=NEW_USER, headers=admin)

    response = client.post("/api/users", json=NEW_USER, headers=admin)

    assert response.status_code == 409
    assert response.json()["detail"] == "A user with this email already exists"


def test_updating_a_user_that_does_not_exist_says_so(client, auth):
    response = client.patch(
        "/api/users/00000000-0000-0000-0000-000000000000", json={"active": False}, headers=auth("admin")
    )

    assert response.status_code == 404
