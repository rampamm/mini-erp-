from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from siam_bean_erp.settings import get_settings

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


def apply_migrations(conn: psycopg.Connection, directory: Path = MIGRATIONS_DIR) -> None:
    conn.execute(
        "create table if not exists schema_migrations ("
        "name text primary key, applied_at timestamptz not null default now())"
    )
    applied = {row["name"] for row in conn.execute("select name from schema_migrations")}
    for path in sorted(directory.glob("*.sql")):
        if path.name in applied:
            continue
        conn.execute(path.read_text())
        conn.execute("insert into schema_migrations (name) values (%s)", (path.name,))


if __name__ == "__main__":
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as connection:
        apply_migrations(connection)
