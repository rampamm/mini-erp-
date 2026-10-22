"""Supabase exposes every table, view and function in `public` through its Data API unless locked down."""


def test_every_public_table_has_row_level_security(conn):
    unprotected = conn.execute(
        "select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace"
        " where n.nspname = 'public' and c.relkind = 'r' and not c.relrowsecurity order by 1"
    ).fetchall()

    assert [r["relname"] for r in unprotected] == []


def test_views_respect_the_row_level_security_of_the_tables_under_them(conn):
    open_views = conn.execute(
        "select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace"
        " where n.nspname = 'public' and c.relkind = 'v'"
        " and not coalesce('security_invoker=true' = any (c.reloptions), false) order by 1"
    ).fetchall()

    assert [r["relname"] for r in open_views] == []


def test_no_function_can_be_called_by_everyone(conn):
    callable_by_public = conn.execute(
        "select p.proname from pg_proc p join pg_namespace n on n.oid = p.pronamespace"
        " where n.nspname = 'public' and (p.proacl is null or exists ("
        "   select 1 from aclexplode(p.proacl) a where a.grantee = 0 and a.privilege_type = 'EXECUTE'))"
        " order by 1"
    ).fetchall()

    assert [r["proname"] for r in callable_by_public] == []
