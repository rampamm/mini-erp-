from fastapi import APIRouter

from siam_bean_erp.deps import Conn, require_roles

router = APIRouter(prefix="/api/users", tags=["users"], dependencies=[require_roles("admin")])


@router.get("")
def list_users(conn: Conn) -> list[dict]:
    return conn.execute(
        "select id, email, full_name, role, active from profiles order by full_name, email"
    ).fetchall()
