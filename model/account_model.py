from model.db import cursor

_ACCOUNT_SELECT = """
SELECT id, name, email, role
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
            SELECT id, name, email, role
            FROM accounts
            WHERE id = %s
            LIMIT 1
            """,
            (account_id,),
        )
        return cur.fetchone()


def create_account(name, email, role):
    with cursor() as cur:
        cur.execute(
            """
            INSERT INTO accounts (name, email, role)
            VALUES (%s, %s, %s)
            """,
            (name.strip(), email.strip(), role.strip()),
        )


def update_account(account_id, name, email, role):
    with cursor() as cur:
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
            SELECT id, name, email, role
            FROM accounts
            WHERE email = %s
            LIMIT 1
            """,
            (email.strip(),),
        )
        return cur.fetchone()
