import time

import jwt
import pytest

from siam_bean_erp.security import create_token, hash_password
from siam_bean_erp.settings import get_settings


def test_login_returns_a_token_and_the_users_role(client, make_user):
    make_user("sales", email="nok@test.local", password_hash=hash_password("secret12"))

    response = client.post("/api/auth/login", json={"email": "nok@test.local", "password": "secret12"})

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "sales"
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.json()["email"] == "nok@test.local"


def test_login_with_the_wrong_password_says_so(client, make_user):
    make_user("sales", email="nok@test.local", password_hash=hash_password("secret12"))

    response = client.post("/api/auth/login", json={"email": "nok@test.local", "password": "nope"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Wrong email or password"


def test_a_deactivated_user_cannot_log_in(client, make_user):
    make_user("sales", active=False, email="gone@test.local", password_hash=hash_password("secret12"))

    response = client.post("/api/auth/login", json={"email": "gone@test.local", "password": "secret12"})

    assert response.status_code == 401


def test_a_token_stops_working_once_the_user_is_deactivated(client, make_user, conn):
    user = make_user("sales")
    headers = {"Authorization": f"Bearer {create_token(user['id'])}"}
    assert client.get("/api/auth/me", headers=headers).status_code == 200

    conn.execute("update profiles set active = false where id = %s", (user["id"],))

    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_requests_without_a_token_are_rejected(client):
    assert client.get("/api/auth/me").status_code == 401


def test_an_expired_or_forged_token_is_rejected(client, make_user):
    user = make_user("admin")
    secret = get_settings().jwt_secret
    claims = {"sub": str(user["id"]), "aud": "authenticated"}
    expired = jwt.encode({**claims, "exp": int(time.time()) - 10}, secret, "HS256")
    forged = jwt.encode({**claims, "exp": int(time.time()) + 600}, "another-secret-another-secret-123456", "HS256")

    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


def test_the_role_comes_from_the_database_not_from_the_token(client, make_user):
    user = make_user("sales")
    secret = get_settings().jwt_secret
    token = jwt.encode(
        {"sub": str(user["id"]), "aud": "authenticated", "role": "admin", "exp": int(time.time()) + 600},
        secret,
        "HS256",
    )

    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403


@pytest.mark.parametrize("role,expected", [("admin", 200), ("sales", 403), ("warehouse", 403), ("accountant", 403)])
def test_only_an_admin_can_list_users(client, auth, role, expected):
    assert client.get("/api/users", headers=auth(role)).status_code == expected


def test_a_403_says_what_happened(client, auth):
    response = client.get("/api/users", headers=auth("sales"))

    assert response.json()["detail"] == "Your role is not allowed to do this"
