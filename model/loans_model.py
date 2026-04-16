from model.db import cursor

_LOAN_SELECT = """
SELECT loans.id, books.title, books.code, authors.name, accounts.name as account_name,
loans.borrow_date, loans.due_date, loans.return_date, loans.status
FROM loans
JOIN books ON loans.books_id = books.id
JOIN authors ON books.author_id = authors.id
LEFT JOIN accounts ON loans.account_id = accounts.id
"""

_LOAN_DETAILED_SELECT = _LOAN_SELECT
def list_borrowing():
    # Lấy danh sách sách đang mượn HOẶC đang chờ duyệt
    with cursor() as cur:
        cur.execute(
            _LOAN_SELECT + " WHERE loans.status IN ('borrowed', 'pending') ORDER BY loans.borrow_date DESC"
        )
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
        cur.execute("SELECT id, name FROM accounts ORDER BY name")
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
        # Chỉ trừ số lượng sách nếu status là 'borrowed' (admin mượn trực tiếp)
        if status == 'borrowed':
            cur.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE id = %s",
                (book_id,)
            )

def approve_loan(loan_id):
    # Admin duyệt đơn mượn
    with cursor() as cur:
        # Lấy books_id từ loan
        cur.execute("SELECT books_id, status FROM loans WHERE id = %s", (loan_id,))
        result = cur.fetchone()
        if result and result['status'] == 'pending':
            book_id = result['books_id']
            # Cập nhật trạng thái thành borrowed
            cur.execute("UPDATE loans SET status = 'borrowed' WHERE id = %s", (loan_id,))
            # CHÍNH THỨC trừ số lượng sách trong kho
            cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id = %s", (book_id,))
            return True
    return False

def return_book(loan_id):
    # Trả sách 
    with cursor() as cur:
        # Lấy books_id từ loan
        cur.execute("SELECT books_id, status FROM loans WHERE id = %s", (loan_id,))
        result = cur.fetchone()
        if result:
            book_id = result['books_id']
            status = result['status']
            # Cập nhật loan sang trạng thái returned
            cur.execute(
                "UPDATE loans SET return_date = CURDATE(), status = 'returned' WHERE id = %s",
                (loan_id,)
            )
            # Nếu trước đó đã mượn (đã trừ kho) thì giờ cộng lại kho
            if status == 'borrowed':
                cur.execute("UPDATE books SET quantity = quantity + 1 WHERE id = %s", (book_id,))
        