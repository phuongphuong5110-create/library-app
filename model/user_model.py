from model.db import cursor
import hashlib

__USER_SELECT = """
SELECT id, username, role
FROM users
ORDER BY username
"""
class User:
    def __init__(self, conn):
        self.conn = conn

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def create_user(self, username, password, email, fullname, role):
        hashed_password = self._hash_password(password)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (username, password, email, fullname, role)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (username.strip(), hashed_password, email.strip(), fullname.strip(), role.strip()),
            )
        self.conn.commit()

    def check_admin_login(self, username, password):
        hashed_password = self._hash_password(password)
        print(hashed_password)
        cursor = self.conn.cursor()

        query = """
        SELECT * FROM users
        WHERE username = %s AND password = %s AND role = 'admin'
        """

        cursor.execute(query, (username, hashed_password))
        return cursor.fetchone()
    
    def check_staff_login(self, username, password):
        hashed_password = self._hash_password(password)
        cursor = self.conn.cursor()

        query = """
        SELECT * FROM users
        WHERE username = %s AND password = %s AND role = 'staff'
        """

        cursor.execute(query, (username, password))
        return cursor.fetchone()