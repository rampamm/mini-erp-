MARKER = "isolation-marker"


def test_a_row_written_in_one_test_is_visible_inside_that_test(conn):
    conn.execute("insert into schema_migrations (name) values (%s)", (MARKER,))

    assert conn.execute(
        "select count(*) from schema_migrations where name = %s", (MARKER,)
    ).fetchone() == (1,)


def test_a_row_written_in_an_earlier_test_is_gone_in_the_next(conn):
    assert conn.execute(
        "select count(*) from schema_migrations where name = %s", (MARKER,)
    ).fetchone() == (0,)
