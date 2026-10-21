import psycopg
from psycopg.rows import dict_row

from siam_bean_erp.reset_db import reset_database

ADMIN_URL = "postgresql://erp:erp@localhost:54329/erp"
SCRATCH_URL = "postgresql://erp:erp@localhost:54329/erp_reset_check"


def test_resetting_a_database_rebuilds_the_schema_and_loads_the_demo_data(test_db_url):
    try:
        reset_database(SCRATCH_URL)
        reset_database(SCRATCH_URL)

        with psycopg.connect(SCRATCH_URL, row_factory=dict_row) as conn:
            skus = [r["sku"] for r in conn.execute("select sku from products order by sku")]
            users = conn.execute("select count(*) as n from profiles").fetchone()["n"]
            on_hand = conn.execute(
                "select s.on_hand from product_stock s join products p on p.id = s.product_id where p.sku = 'ARB-1KG'"
            ).fetchone()["on_hand"]
        assert skus == ["ARB-1KG", "BLD-1KG", "DRP-10", "ROB-1KG"]
        assert (users, on_hand) == (5, 170)
    finally:
        with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
            admin.execute("drop database if exists erp_reset_check with (force)")
