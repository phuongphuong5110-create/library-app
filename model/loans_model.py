from model.db import cursor
from datetime import datetime

_LOAN_SELECT = """
SELECT loans.id, books.title, books.code, authors.name, accounts.name as account_name,
loans.borrow_date, loans.due_date, loans.return_date, loans.status
FROM loans
JOIN books ON loans.books_id = books.id
JOIN authors ON books.author_id = authors.id
LEFT JOIN accounts ON loans.account_id = accounts.id
"""

_LOAN_DETAILED_SELECT = _LOAN_SELECT
def list_borrowing(account_id=None):
    # Lấy danh sách sách mượn
    sql = _LOAN_SELECT + " WHERE 1=1"
    params = []
    
    if account_id:
        sql += " AND loans.account_id = %s"
        params.append(account_id)
        
    sql += " ORDER BY loans.borrow_date DESC"
    
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def list_returned():
    # Lấy danh sách sách đã trả
    with cursor() as cur:
        cur.execute(
            _LOAN_DETAILED_SELECT + " WHERE loans.status = 'returned' ORDER BY loans.return_date DESC"
        )
        return cur.fetchall()

def list_available_books():
    # Lấy danh sách tất cả sách để mượn
    with cursor() as cur:
        cur.execute("""
            SELECT id, title, code, author_id, quantity
            FROM books
            ORDER BY title
        """)
        return cur.fetchall()

def search_books(search_text):
    # Tìm kiếm sách theo tên
    with cursor() as cur:
        cur.execute("""
            SELECT id, title, code, author_id, quantity
            FROM books
            WHERE title LIKE %s
            ORDER BY title
        """, (f"%{search_text}%",))
        return cur.fetchall()

def get_accounts():
    # Lấy danh sách người dùng
    with cursor() as cur:
        cur.execute("SELECT id, name, email FROM accounts ORDER BY name")
        return cur.fetchall()

def borrow_book(book_id, account_id, due_date, status='borrowed'):
    # Tạo danh sách mượn sách
    with cursor() as cur:
        # Thêm loan record
        cur.execute(
            """
            INSERT INTO loans (books_id, authors_id, account_id, borrow_date, due_date, status)
            VALUES (%s, (SELECT author_id FROM books WHERE id = %s), %s, CURDATE(), %s, %s)
            """,
            (book_id, book_id, account_id, due_date, status),
        )
        if status == 'borrowed':
            cur.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE id = %s",
                (book_id,)
            )

def approve_loan(loan_id):
    with cursor() as cur:
        cur.execute("SELECT books_id, status FROM loans WHERE id = %s", (loan_id,))
        result = cur.fetchone()
        if result and result['status'] == 'pending':
            book_id = result['books_id']
            cur.execute("UPDATE loans SET status = 'borrowed' WHERE id = %s", (loan_id,))
            cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id = %s", (book_id,))
            return True
    return False

def return_book(loan_id):
    with cursor() as cur:
        cur.execute("SELECT books_id, status FROM loans WHERE id = %s", (loan_id,))
        result = cur.fetchone()
        if result:
            book_id = result['books_id']
            status = result['status']
            cur.execute(
                "UPDATE loans SET return_date = CURDATE(), status = 'returned' WHERE id = %s",
                (loan_id,)
            )
            if status == 'borrowed':
                cur.execute("UPDATE books SET quantity = quantity + 1 WHERE id = %s", (book_id,))

def overdue_book(loan_id):
    with cursor() as cur:
        cur.execute("SELECT due_date, status FROM loans WHERE id = %s", (loan_id,))
        result = cur.fetchone()
        if result:
            to_date = result['due_date']
            status = result['status']
            
            if datetime.now().date() > to_date and status == 'borrowed':
                cur.execute("UPDATE loans SET status = 'overdue' WHERE id = %s", (loan_id,))
                return True
    return False

def check_and_update_overdue():
    """Cập nhật tất cả các khoản mượn đã quá hạn từ 'borrowed' sang 'overdue'"""
    with cursor() as cur:
        cur.execute("""
            UPDATE loans 
            SET status = 'overdue' 
            WHERE status = 'borrowed' AND due_date < CURDATE()
        """)