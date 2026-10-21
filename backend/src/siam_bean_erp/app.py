from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI

from siam_bean_erp.db import get_conn


def create_app() -> FastAPI:
    app = FastAPI(title="Siam Bean ERP")

    @app.get("/api/health")
    def health(conn: Annotated[psycopg.Connection, Depends(get_conn)]) -> dict[str, str]:
        conn.execute("select 1")
        return {"status": "ok", "db": "ok"}

    return app
