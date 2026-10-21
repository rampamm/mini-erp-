import itertools
import os

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from siam_bean_erp.app import create_app
from siam_bean_erp.db import get_conn
from siam_bean_erp.migrate import apply_migrations
from siam_bean_erp.security import create_token

ADMIN_URL = os.environ.get("TEST_ADMIN_URL", "postgresql://erp:erp@localhost:54329/erp")
TEST_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://erp:erp@localhost:54329/erp_test")

ROLES = ("admin", "sales", "warehouse", "accountant")


@pytest.fixture(scope="session")
def test_db_url():
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        exists = admin.execute("select 1 from pg_database where datname = 'erp_test'").fetchone()
        if not exists:
            admin.execute("create database erp_test")
    with psycopg.connect(TEST_URL, autocommit=True, row_factory=dict_row) as conn:
        apply_migrations(conn)
    return TEST_URL


@pytest.fixture
def conn(test_db_url):
    connection = psycopg.connect(test_db_url, row_factory=dict_row)
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.fixture
def client(conn):
    app = create_app()
    app.dependency_overrides[get_conn] = lambda: conn
    return TestClient(app)


_counter = itertools.count(1)


@pytest.fixture
def make_user(conn):
    def _make(role="sales", active=True, password_hash=None, email=None):
        n = next(_counter)
        return conn.execute(
            "insert into profiles (email, full_name, role, active, password_hash)"
            " values (%s, %s, %s, %s, %s) returning *",
            (email or f"{role}{n}@test.local", f"{role.title()} {n}", role, active, password_hash),
        ).fetchone()

    return _make


@pytest.fixture
def auth(make_user):
    """Headers for a fresh user with the given role."""

    def _auth(role):
        return {"Authorization": f"Bearer {create_token(make_user(role)['id'])}"}

    return _auth
