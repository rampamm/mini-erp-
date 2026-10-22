"""Drop and rebuild a database from the migrations, then load the demo data.

Usage: python -m siam_bean_erp.reset_db   (uses DATABASE_URL)
"""

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.rows import dict_row

from siam_bean_erp.migrate import apply_migrations
from siam_bean_erp.seed import seed
from siam_bean_erp.settings import get_settings

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", ""}


def reset_database(url: str) -> None:
    info = conninfo_to_dict(url)
    if info.get("host", "") not in LOCAL_HOSTS:
        raise SystemExit("Refusing to reset a database that is not local. This tool drops the whole database.")
    name = info["dbname"]
    maintenance = make_conninfo(url, dbname="postgres")
    with psycopg.connect(maintenance, autocommit=True) as admin:
        admin.execute(sql.SQL("drop database if exists {} with (force)").format(sql.Identifier(name)))
        admin.execute(sql.SQL("create database {}").format(sql.Identifier(name)))
    with psycopg.connect(url, row_factory=dict_row) as conn:
        apply_migrations(conn)
        seed(conn)


if __name__ == "__main__":
    target = get_settings().database_url
    reset_database(target)
    print(f"Reset {conninfo_to_dict(target)['dbname']}: schema rebuilt and demo data loaded.")
