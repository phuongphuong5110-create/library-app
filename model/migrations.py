from model.db import cursor


def _has_column(table_name: str, column_name: str) -> bool:
    with cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS c
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
            """,
            (table_name, column_name),
        )
        row = cur.fetchone()
        return bool(row and row.get("c"))


def ensure_latest_schema():
    """
    Keep schema compatible for existing databases.
    This is intentionally small and additive-only.
    """
    if not _has_column("books", "cover_path"):
        with cursor() as cur:
            cur.execute("ALTER TABLE books ADD COLUMN cover_path VARCHAR(255) NULL")

