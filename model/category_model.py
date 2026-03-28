from model.db import cursor


def count_all():
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM categories")
        return cur.fetchone()["c"]


def list_rows():
    with cursor() as cur:
        cur.execute(
            "SELECT id, category_name FROM categories ORDER BY category_name"
        )
        return cur.fetchall()


def insert(category_name):
    with cursor() as cur:
        cur.execute(
            "INSERT INTO categories (category_name) VALUES (%s)",
            (category_name.strip(),),
        )


def names_for_combobox():
    rows = list_rows()
    return [(r["id"], r["category_name"]) for r in rows]


def update_row(row_id, category_name):
    with cursor() as cur:
        cur.execute(
            "UPDATE categories SET category_name = %s WHERE id = %s",
            (category_name.strip(), row_id),
        )


def delete_by_id(row_id):
    with cursor() as cur:
        cur.execute("DELETE FROM categories WHERE id = %s", (row_id,))
