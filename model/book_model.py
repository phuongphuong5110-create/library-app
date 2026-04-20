from model.db import cursor

_BOOK_SELECT = """
SELECT b.id, b.title, b.code, b.quantity, b.year, b.description, b.cover_path,
       b.category_id, b.author_id, b.publisher_id,
       c.category_name, a.name AS author_name, p.name AS publisher_name
FROM books b
JOIN categories c ON b.category_id = c.id
JOIN authors a ON b.author_id = a.id
JOIN publishers p ON b.publisher_id = p.id
"""


def count_all():
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM books")
        return cur.fetchone()["c"]


def list_for_stats_table():
    with cursor() as cur:
        cur.execute(
            f"""
            {_BOOK_SELECT}
            ORDER BY b.title
            """
        )
        return cur.fetchall()


def insert_book(
    title,
    code,
    quantity,
    year,
    description,
    category_id,
    author_id,
    publisher_id,
    cover_path=None,
):
    with cursor() as cur:
        cur.execute(
            """
            INSERT INTO books (
                title, code, quantity, year, description, cover_path,
                category_id, author_id, publisher_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                title.strip(),
                code.strip(),
                quantity,
                year,
                description or "",
                cover_path,
                category_id,
                author_id,
                publisher_id,
            ),
        )


def find_by_title(title):
    with cursor() as cur:
        cur.execute(
            f"""
            {_BOOK_SELECT}
            WHERE b.title = %s
            LIMIT 1
            """,
            (title.strip(),),
        )
        return cur.fetchone()


def find_by_id(book_id):
    with cursor() as cur:
        cur.execute(
            f"""
            {_BOOK_SELECT}
            WHERE b.id = %s
            LIMIT 1
            """,
            (book_id,),
        )
        return cur.fetchone()


def update_book(
    book_id,
    title,
    code,
    quantity,
    year,
    description,
    category_id,
    author_id,
    publisher_id,
    cover_path=None,
):
    with cursor() as cur:
        cur.execute(
            """
            UPDATE books SET
                title = %s, code = %s, quantity = %s, year = %s, description = %s, cover_path = %s,
                category_id = %s, author_id = %s, publisher_id = %s
            WHERE id = %s
            """,
            (
                title.strip(),
                code.strip(),
                quantity,
                year,
                description or "",
                cover_path,
                category_id,
                author_id,
                publisher_id,
                book_id,
            ),
        )


def list_available(search_text=None):
    sql = f"""
        {_BOOK_SELECT}
        WHERE b.quantity > 0
    """
    params = []
    if search_text:
        q = f"%{search_text.strip()}%"
        sql += " AND (b.title LIKE %s OR b.code LIKE %s)"
        params.extend([q, q])
    sql += " ORDER BY b.title"
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def delete_by_id(book_id):
    with cursor() as cur:
        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
