from siam_bean_erp.migrate import apply_migrations


def test_running_migrations_twice_applies_each_file_only_once(conn, tmp_path):
    (tmp_path / "9999_widgets.sql").write_text(
        "create table widgets (id int primary key);\ninsert into widgets values (1);"
    )

    apply_migrations(conn, tmp_path)
    apply_migrations(conn, tmp_path)

    assert conn.execute("select count(*) from widgets").fetchone() == (1,)
    assert conn.execute(
        "select count(*) from schema_migrations where name = '9999_widgets.sql'"
    ).fetchone() == (1,)
