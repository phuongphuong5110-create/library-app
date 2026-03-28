import pymysql

from app_config import load_database_config


def run_schema_statements(conn):
    cur = conn.cursor()
    schema_path = __import__("pathlib").Path(__file__).resolve().parent / "sql" / "schema.sql"
    text = schema_path.read_text(encoding="utf-8")
    statements = []
    buf = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        buf.append(line)
        if line.rstrip().endswith(";"):
            statements.append("\n".join(buf))
            buf = []
    if buf:
        statements.append("\n".join(buf))
    for stmt in statements:
        cur.execute(stmt)
    conn.commit()


def main():
    cfg = load_database_config()
    conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        charset=cfg["charset"],
    )
    try:
        run_schema_statements(conn)
        print("Schema applied successfully.")
    except pymysql.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
