import sys

new_content = """from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog
from PyQt5 import uic
from pathlib import Path
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
        self.dialog = None
        
        try:
            self.screen.btn_search_book_return.clicked.connect(self._load_borrowing_list)
            self.screen.btn_return_book.clicked.connect(self.return_book)
            if hasattr(self.screen, 'btn_dialog_loans'):
                self.screen.btn_dialog_loans.clicked.connect(self.open_add_loan_dialog)
        except Exception as e:
            print(f"Lỗi kết nối button trên screen_loans: {e}")
        
        self.refresh_return_table()

    def open_add_loan_dialog(self):
        self.dialog = QDialog(self.main_window)
        _VIEW_DIR = Path(__file__).resolve().parent.parent / "view"
        uic.loadUi(str(_VIEW_DIR / "dialog_loans.ui"), self.dialog)
        
        try:
            self.dialog.btn_confirm_loans.clicked.connect(self.borrow_book_action)
            self.dialog.btn_cancel_loans.clicked.connect(self.dialog.reject)
            self.dialog.btn_addbook_loans.clicked.connect(self.add_book_to_list)
            self.dialog.search_book_borrow.textChanged.connect(self._search_available_books)
        except Exception as e:
            print(f"Lỗi kết nối button trong dialog_loans: {e}")
            
        self.dialog.user_borrow.setText("")
        self.dialog.email_account.setText("")
        self.dialog.list_book_borrow.clear()
        self.dialog.search_book_borrow.setText("")
        self.dialog.note_loans.setText("")
        self.dialog.borrow_date.setDate(datetime.now())
        self.dialog.return_date.setDate(datetime.now())
        
        self.refresh_borrow_table_dialog()
        self.dialog.exec_()

    def refresh_borrow_table_dialog(self):
        try:
            rows = loans_model.list_available_books()
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Lỗi: {str(e)}")
            print("ERROR:", e)
            return
        
        t = self.dialog.table_loans_return
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(str(row["code"])))
            status = "Đang còn" if row['quantity'] > 0 else "Hết"
            t.setItem(r, 3, QTableWidgetItem(status))

    def refresh_return_table(self):
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
        search_text = self.dialog.search_book_borrow.text().strip()
        if not search_text:
            self.refresh_borrow_table_dialog()
            return
        
        try:
            rows = loans_model.search_books(search_text)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi tìm kiếm: {str(e)}")
            return
        
        t = self.dialog.table_loans_return
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(str(row["code"])))
            status = "Đang còn" if row['quantity'] > 0 else "Hết"
            t.setItem(r, 3, QTableWidgetItem(status))

    def _load_borrowing_list(self):
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

    def return_book(self):
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
            self.refresh_return_table()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi trả sách: {str(e)}")
            
    def borrow_book_action(self):
        list_widget = self.dialog.list_book_borrow
        if list_widget.count() == 0:
            QMessageBox.warning(self.main_window, "Thông báo", "Vui lòng chọn sách và bấm 'Thêm Sách' vào danh sách mượn!")
            return
            
        user_name = self.dialog.user_borrow.text().strip()
        user_email = self.dialog.email_account.text().strip()
        
        if not user_name or not user_email:
            QMessageBox.warning(self.main_window, "Thông báo", "Vui lòng nhập đầy đủ Tên người mượn và Email!")
            return
            
        from model import account_model
        acc = account_model.find_by_email(user_email)
        if acc:
            account_id = acc['id']
        else:
            try:
                account_model.create_account(user_name, user_email, "Người đọc")
                acc = account_model.find_by_email(user_email)
                account_id = acc['id']
            except Exception as e:
                QMessageBox.critical(self.main_window, "Lỗi", f"Không thể tạo tài khoản mới: {e}")
                return
            
        due_date = self.dialog.return_date.date().toString("yyyy-MM-dd")
        
        success_count = 0
        try:
            for i in range(list_widget.count()):
                item_text = list_widget.item(i).text()
                book_id = int(item_text.split(" - ")[0])
                loans_model.borrow_book(book_id, account_id, due_date)
                success_count += 1
            
            QMessageBox.information(self.main_window, "Thành công", f"Đã mượn thành công {success_count} quyển sách!")
            self.dialog.accept()
            self.refresh_return_table()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Có lỗi xảy ra (kiểm tra ID người mượn có tồn tại không). Chi tiết: {e}")

    def add_book_to_list(self):
        selected_rows = self.dialog.table_loans_return.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.main_window, "Thông báo", "Vui lòng chọn ít nhất 1 sách từ bảng để thêm!")
            return
            
        for row in selected_rows:
            row_idx = row.row()
            book_id = self.dialog.table_loans_return.item(row_idx, 0).text()
            book_title = self.dialog.table_loans_return.item(row_idx, 1).text()
            item_text = f"{book_id} - {book_title}"
            
            exists = False
            for i in range(self.dialog.list_book_borrow.count()):
                if self.dialog.list_book_borrow.item(i).text() == item_text:
                    exists = True
                    break
            
            if not exists:
                self.dialog.list_book_borrow.addItem(item_text)
"""

with open('/Users/macos/Python/thuchanh/app/appthuvien/controller/loans_controller.py', 'w') as f:
    f.write(new_content)
print("Updated successfully")
