import psycopg
from psycopg.rows import dict_row

from siam_bean_erp.security import hash_password
from siam_bean_erp.settings import get_settings

DEMO_PASSWORD = "demo1234"

DEMO_USERS = [
    ("somchai@siambean.test", "Khun Somchai", "admin"),
    ("nok@siambean.test", "Nok", "sales"),
    ("ploy@siambean.test", "Ploy", "sales"),
    ("lek@siambean.test", "Lek", "warehouse"),
    ("fon@siambean.test", "Fon", "accountant"),
]


def seed(conn: psycopg.Connection) -> None:
    password_hash = hash_password(DEMO_PASSWORD)
    for email, full_name, role in DEMO_USERS:
        conn.execute(
            "insert into profiles (email, full_name, role, password_hash) values (%s, %s, %s, %s)"
            " on conflict (email) do nothing",
            (email, full_name, role, password_hash),
        )


if __name__ == "__main__":
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as connection:
        seed(connection)
    print("Seeded demo data. Demo password for every account:", DEMO_PASSWORD)
