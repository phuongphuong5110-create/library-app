import pymysql
from contextlib import contextmanager

from app_config import load_database_config


def get_connection():
    cfg = load_database_config()
    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset=cfg["charset"],
        cursorclass=pymysql.cursors.DictCursor,
    )


@contextmanager
def cursor():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        yield cur
        conn.commit()
    except pymysql.Error:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
