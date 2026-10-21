from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI

from siam_bean_erp.db import get_conn
from siam_bean_erp.errors import install_error_handlers
from siam_bean_erp.routers import auth, customers, orders, products, stock, users


def create_app() -> FastAPI:
    app = FastAPI(title="Siam Bean ERP")
    install_error_handlers(app)

    @app.get("/api/health")
    def health(conn: Annotated[psycopg.Connection, Depends(get_conn)]) -> dict[str, str]:
        conn.execute("select 1")
        return {"status": "ok", "db": "ok"}

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(products.router)
    app.include_router(customers.router)
    app.include_router(stock.router)
    app.include_router(orders.router)
    return app
