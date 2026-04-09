from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from datetime import datetime, timedelta
import csv
import os

from controller.combo_utils import fill_combobox_with_ids, set_combo_current_data
from model import loans_model
import pymysql

def _parse_int(text, default=0):
    text = (text or "").strip()
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default

class LoansController:
    TAB_LIST = 0
    TAB_ADD = 1
    TAB_EDIT = 2

    def __init__(self, main_window: QMainWindow, screen):
        self.main_window = main_window
        self.screen = screen
        self._selected_loan_id = None
        self._selected_book_id = None
        
        try:
            self.screen.btn_search_book_borrow.clicked.connect(self._search_available_books)
            self.screen.btn_search_book_return.clicked.connect(self._load_borrowing_list)
            self.screen.btn_borrow_book.clicked.connect(self.borrow_book)
            self.screen.btn_return_book.clicked.connect(self.return_book)
        except Exception as e:
            print(f"Lỗi kết nối button: {e}")
        
        self.refresh_borrow_table()
        self.refresh_return_table()

    #Hiển thị danh sách sách có sẵn để mượn
    def refresh_borrow_table(self):
        try:
            rows = loans_model.list_available_books()
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Lỗi: {str(e)}")
            print("ERROR:", e)
            return
        
        t = self.screen.table_loans
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(str(row["code"])))
            status = "Đang còn" if row['quantity'] > 0 else "Hết"
            t.setItem(r, 3, QTableWidgetItem(status))

    def refresh_return_table(self):
        #Hiển thị danh sách sách đang mượn để trả
        try:
            rows = loans_model.list_borrowing()
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Lỗi: {str(e)}")
            print("ERROR:", e)
            return
        
        t = self.screen.table_loans_return
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(row.get("account_name", "")))
            t.setItem(r, 3, QTableWidgetItem(str(row["borrow_date"])))
            t.setItem(r, 4, QTableWidgetItem(str(row["due_date"] or "")))
            t.setItem(r, 5, QTableWidgetItem(self._format_loan_status(row.get("status"))))

    def _format_loan_status(self, status):
        if status == 'borrowed':
            return 'Đã mượn'
        if status == 'returned':
            return 'Đã trả'
        return str(status or '')

    def _search_available_books(self):
        #Tìm kiếm sách theo tên
        search_text = self.screen.search_book.text().strip()
        if not search_text:
            self.refresh_borrow_table()
            return
        
        try:
            rows = loans_model.search_books(search_text)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi tìm kiếm: {str(e)}")
            return
        
        t = self.screen.table_loans
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(str(row["code"])))
            status = "Đang còn" if row['quantity'] > 0 else "Hết"
            t.setItem(r, 3, QTableWidgetItem(status))

    def _load_borrowing_list(self):
        #Tải danh sách sách đang mượn
        search_text = self.screen.search_book_return.text().strip()
        if search_text:
            try:
                rows = loans_model.list_borrowing()
                rows = [r for r in rows if search_text.lower() in r['title'].lower()]
            except Exception as e:
                QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi tìm kiếm: {str(e)}")
                return
        else:
            self.refresh_return_table()
            return
        
        t = self.screen.table_loans_return
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(row.get("account_name", "")))
            t.setItem(r, 3, QTableWidgetItem(str(row["borrow_date"])))
            t.setItem(r, 4, QTableWidgetItem(str(row["due_date"] or "")))
            t.setItem(r, 5, QTableWidgetItem(self._format_loan_status(row.get("status"))))
        
    def borrow_book(self):
        #Mượn sách
        # Lấy dòng được chọn từ bảng sách
        selected_rows = self.screen.table_loans.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.main_window, "Thông báo", "Vui lòng chọn sách để mượn!")
            return
        
        row_idx = selected_rows[0].row()
        book_id = int(self.screen.table_loans.item(row_idx, 0).text())
        book_title = self.screen.table_loans.item(row_idx, 1).text()
        
        # Chọn người mượn
        user_id, ok = self._select_account()
        if not ok or not user_id:
            return
        
        # Chọn ngày trả dự kiến 
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            loans_model.borrow_book(book_id, user_id, due_date)
            QMessageBox.information(self.main_window, "Thành công", f"Mượn '{book_title}' thành công!")
            self.refresh_borrow_table()
            self.refresh_return_table()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi mượn sách: {str(e)}")

    def return_book(self):
        #Trả sách
        # Lấy dòng được chọn từ bảng trả
        selected_rows = self.screen.table_loans_return.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.main_window, "Thông báo", "Vui lòng chọn sách để trả!")
            return
        
        row_idx = selected_rows[0].row()
        loan_id = int(self.screen.table_loans_return.item(row_idx, 0).text())
        book_title = self.screen.table_loans_return.item(row_idx, 1).text()
        
        try:
            loans_model.return_book(loan_id)
            QMessageBox.information(self.main_window, "Thành công", f"Trả '{book_title}' thành công!")
            self.refresh_borrow_table()
            self.refresh_return_table()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi trả sách: {str(e)}")

    def _select_account(self):
        #Hiển thị dialog để chọn người mượn
        try:
            accounts = loans_model.get_accounts()
            account_names = [f"{acc['id']} - {acc['name']}" for acc in accounts]
            
            from PyQt5.QtWidgets import QInputDialog
            account_text, ok = QInputDialog.getItem(
                self.main_window, 
                "Chọn người mượn", 
                "Người dùng:",
                account_names,
                0,
                False
            )
            
            if ok and account_text:
                account_id = int(account_text.split(" - ")[0])
                return account_id, ok
            return None, ok
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi lấy danh sách người dùng: {str(e)}")
            return None, False
