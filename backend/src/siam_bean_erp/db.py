from collections.abc import Iterator

import psycopg

from siam_bean_erp.settings import get_settings


def get_conn() -> Iterator[psycopg.Connection]:
    with psycopg.connect(get_settings().database_url) as conn:
        yield conn
