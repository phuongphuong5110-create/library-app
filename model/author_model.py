from model.db import cursor


def count_all():
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM authors")
        return cur.fetchone()["c"]


def list_rows():
    with cursor() as cur:
        cur.execute("SELECT id, name FROM authors ORDER BY name")
        return cur.fetchall()


def insert(name):
    with cursor() as cur:
        cur.execute("INSERT INTO authors (name) VALUES (%s)", (name.strip(),))


def names_for_combobox():
    rows = list_rows()
    return [(r["id"], r["name"]) for r in rows]


def update_row(row_id, name):
    with cursor() as cur:
        cur.execute(
            "UPDATE authors SET name = %s WHERE id = %s",
            (name.strip(), row_id),
        )


def delete_by_id(row_id):
    with cursor() as cur:
        cur.execute("DELETE FROM authors WHERE id = %s", (row_id,))
