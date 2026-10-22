import importlib

import pytest
from fastapi import FastAPI

from siam_bean_erp.reset_db import reset_database
from siam_bean_erp.settings import DEFAULT_JWT_SECRET, Settings


def test_the_vercel_entrypoint_exposes_the_app():
    index = importlib.import_module("index")

    assert isinstance(index.app, FastAPI)
    assert "/api/health" in index.app.openapi()["paths"]


def test_a_deployed_app_refuses_to_run_with_the_built_in_jwt_secret(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(_env_file=None)


def test_a_deployed_app_accepts_a_real_jwt_secret(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("JWT_SECRET", "x" * 40)

    assert Settings(_env_file=None).jwt_secret == "x" * 40


def test_the_built_in_secret_is_fine_on_a_developer_machine(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)

    assert Settings(_env_file=None).jwt_secret == DEFAULT_JWT_SECRET


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://postgres.abc:pw@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres",
        "postgresql://postgres:pw@db.abcdefgh.supabase.co:5432/postgres",
    ],
)
def test_reset_refuses_to_wipe_a_database_that_is_not_local(url):
    with pytest.raises(SystemExit, match="local"):
        reset_database(url)
