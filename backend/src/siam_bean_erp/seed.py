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

DEMO_CUSTOMERS = [
    ("Café Lune", "0105561000011", "30 days"),
    ("Brew Lab Ari", "0105562000022", "Cash"),
    ("Sukhumvit Corner Café", "0105563000033", "15 days"),
]

OPENING_STOCK = {"ARB-1KG": 170, "ROB-1KG": 35, "BLD-1KG": 90, "DRP-10": 240}


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
    for name, tax_id, payment_terms in DEMO_CUSTOMERS:
        conn.execute(
            "insert into customers (name, tax_id, payment_terms)"
            " select %s, %s, %s where not exists (select 1 from customers where tax_id = %s)",
            (name, tax_id, payment_terms, tax_id),
        )
    for sku, quantity in OPENING_STOCK.items():
        conn.execute(
            "insert into stock_movements (product_id, movement_type, quantity, reason, user_id)"
            " select p.id, 'stock_in', %s, 'Opening stock', u.id from products p, profiles u"
            " where p.sku = %s and u.email = 'lek@siambean.test'"
            " and not exists (select 1 from stock_movements m where m.product_id = p.id and m.reason = 'Opening stock')",
            (quantity, sku),
        )


if __name__ == "__main__":
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as connection:
        seed(connection)
    print("Seeded demo data. Demo password for every account:", DEMO_PASSWORD)
