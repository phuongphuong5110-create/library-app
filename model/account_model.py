from model.db import cursor
import hashlib

_ACCOUNT_SELECT = """
SELECT id, name, email, role, username, password
FROM accounts
ORDER BY name 
"""


def list_all_accounts():
    with cursor() as cur:
        cur.execute(_ACCOUNT_SELECT)
        return cur.fetchall()


def find_by_id(account_id):
    with cursor() as cur:
        cur.execute(
            """
            SELECT id, name, email, role, username
            FROM accounts
            WHERE id = %s
            LIMIT 1
            """,
            (account_id,),
        )
        return cur.fetchone()


def create_account(name, email, role, username=None, password=None):
    with cursor() as cur:
        cur.execute(
            """
            INSERT INTO accounts (name, email, role, username, password)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name.strip(), email.strip(), role.strip(), username, password),
        )


def update_account(account_id, name, email, role, username=None):
    with cursor() as cur:
        if username:
            cur.execute(
                """
                UPDATE accounts SET
                    name = %s, email = %s, role = %s, username = %s
                WHERE id = %s
                """,
                (name.strip(), email.strip(), role.strip(), username.strip(), account_id),
            )
        else:
            cur.execute(
                """
                UPDATE accounts SET
                    name = %s, email = %s, role = %s
                WHERE id = %s
                """,
                (name.strip(), email.strip(), role.strip(), account_id),
            )


def delete_by_id(account_id):
    with cursor() as cur:
        cur.execute("DELETE FROM accounts WHERE id = %s", (account_id,))


def count_all():
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM accounts")
        return cur.fetchone()["c"]


def find_by_email(email):
    with cursor() as cur:
        cur.execute(
            """
            SELECT id, name, email, role, username
            FROM accounts
            WHERE email = %s
            LIMIT 1
            """,
            (email.strip(),),
        )
        return cur.fetchone()


def find_by_username(username):
    if not username:
        return None
    with cursor() as cur:
        cur.execute(
            """
            SELECT id, name, email, role, username
            FROM accounts
            WHERE username = %s
            LIMIT 1
            """,
            (username.strip(),),
        )
        return cur.fetchone()

class Account:
    def __init__(self, conn):
        self.conn = conn

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def create_user(self, username, password, role):
        hashed_password = self._hash_password(password)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO accounts (username, password, role)
                VALUES (%s, %s, %s)
                """,
                (username.strip(), hashed_password, role.strip()),
            )
        self.conn.commit()

    def check_admin_login(self, username, password):
        hashed_password = self._hash_password(password)
        cursor = self.conn.cursor()
        # Kiểm tra cả 'admin' và 'Admin'
        query = "SELECT * FROM accounts WHERE username = %s AND password = %s AND (role = 'admin' OR role = 'Admin')"
        cursor.execute(query, (username, hashed_password))
        return cursor.fetchone()

    def check_reader_login(self, username, password):
        hashed_password = self._hash_password(password)
        cursor = self.conn.cursor()
        # Kiểm tra các biến thể role đang dùng trong DB và chuẩn hoá về 'reader'
        query = """
            SELECT *
            FROM accounts
            WHERE username = %s AND password = %s
              AND (
                role = 'reader' OR role = 'Reader'
                OR role = 'Người dùng' OR role = 'người dùng'
                OR role = 'Người đọc' OR role = 'người đọc'
              )
        """
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()
        if user:
            user["role"] = "reader"
        return user
