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

DEMO_PRODUCTS = [
    ("ARB-1KG", "Arabica, 1 kg bag", "kg", 320, 450, 50),
    ("ROB-1KG", "Robusta, 1 kg bag", "kg", 220, 320, 40),
    ("BLD-1KG", "House Blend, 1 kg bag", "kg", 260, 380, 30),
    ("DRP-10", "Drip bags, box of 10", "box", 90, 150, 100),
]


def seed(conn: psycopg.Connection) -> None:
    password_hash = hash_password(DEMO_PASSWORD)
    for email, full_name, role in DEMO_USERS:
        conn.execute(
            "insert into profiles (email, full_name, role, password_hash) values (%s, %s, %s, %s)"
            " on conflict (email) do nothing",
            (email, full_name, role, password_hash),
        )
    for sku, name, unit, cost, price, reorder_level in DEMO_PRODUCTS:
        conn.execute(
            "insert into products (sku, name, unit, cost, price, reorder_level)"
            " values (%s, %s, %s, %s, %s, %s) on conflict (sku) do nothing",
            (sku, name, unit, cost, price, reorder_level),
        )


if __name__ == "__main__":
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as connection:
        seed(connection)
    print("Seeded demo data. Demo password for every account:", DEMO_PASSWORD)
