from collections.abc import Iterator

import psycopg
from psycopg.rows import dict_row

from siam_bean_erp.settings import get_settings


def get_conn() -> Iterator[psycopg.Connection]:
    # prepare_threshold=None: Supabase's transaction pooler (port 6543) does not support prepared statements.
    with psycopg.connect(get_settings().database_url, row_factory=dict_row, prepare_threshold=None) as conn:
        yield conn
