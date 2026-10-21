import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from siam_bean_erp.app import create_app
from siam_bean_erp.db import get_conn
from siam_bean_erp.migrate import apply_migrations

ADMIN_URL = os.environ.get("TEST_ADMIN_URL", "postgresql://erp:erp@localhost:54329/erp")
TEST_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://erp:erp@localhost:54329/erp_test")


@pytest.fixture(scope="session")
def test_db_url():
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        exists = admin.execute("select 1 from pg_database where datname = 'erp_test'").fetchone()
        if not exists:
            admin.execute("create database erp_test")
    with psycopg.connect(TEST_URL, autocommit=True) as conn:
        apply_migrations(conn)
    return TEST_URL


@pytest.fixture
def conn(test_db_url):
    connection = psycopg.connect(test_db_url)
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
