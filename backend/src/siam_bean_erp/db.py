from collections.abc import Iterator

import psycopg
from psycopg.rows import dict_row

from siam_bean_erp.settings import get_settings


def get_conn() -> Iterator[psycopg.Connection]:
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as conn:
        yield conn
