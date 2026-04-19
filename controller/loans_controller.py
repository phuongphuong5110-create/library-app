from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
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
            self.screen.btn_approve_loan.clicked.connect(self.approve_loan_action)
            
            #Chỉ admin thấy nút Duyệt
            user = getattr(self.main_window, '_current_user', {})
            role = str(user.get('role') or '').lower()
            if role != 'admin':
                self.screen.btn_approve_loan.hide()

            if hasattr(self.screen, 'btn_dialog_loans'):
                self.screen.btn_dialog_loans.clicked.connect(self.open_add_loan_dialog)
            
            #các bộ lọc
            self.screen.combo_filter_status.currentIndexChanged.connect(self._load_borrowing_list)
            self.screen.combo_filter_borrower.currentIndexChanged.connect(self._load_borrowing_list)
            self.screen.combo_filter_date.currentIndexChanged.connect(self._load_borrowing_list)
        except Exception as e:
            print(f"Lỗi kết nối button trên screen_loans: {e}")
        
        self.refresh_return_table()
        self._populate_filter_combos()

    def open_add_loan_dialog(self):
        self.dialog = QDialog(self.main_window)
        _VIEW_DIR = Path(__file__).resolve().parent.parent / "view"
        uic.loadUi(str(_VIEW_DIR / "dialog_loans.ui"), self.dialog)
        
        try:
            self.dialog.btn_confirm_loans.clicked.connect(self.borrow_book_action)
            self.dialog.btn_cancel_loans.clicked.connect(self.dialog.reject)
            self.dialog.btn_addbook_loans.clicked.connect(self.add_book_to_list)
            self.dialog.search_book_borrow.textChanged.connect(self._search_available_books)
            self.dialog.user_borrow.activated.connect(self._on_borrower_changed)
        except Exception as e:
            print(f"Lỗi kết nối button trong dialog_loans: {e}")
            
        # Lấy thông tin user hiện tại
        user = getattr(self.main_window, '_current_user', {})
        role = str(user.get('role') or '').lower()

        if role == 'reader' or role == 'người dùng':
            self.dialog.user_borrow.clear()
            self.dialog.user_borrow.addItem(user.get('name', ''), user)
            self.dialog.user_borrow.setCurrentIndex(0)
            self.dialog.user_borrow.setEnabled(False) 
            
            p = self.dialog.user_borrow.palette()
            p.setColor(QPalette.Disabled, QPalette.Text, Qt.black)
            p.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.black)
            p.setColor(QPalette.Disabled, QPalette.WindowText, Qt.black)
            self.dialog.user_borrow.setPalette(p)
            
            self.dialog.email_account.setText(user.get('email', ''))
            self.dialog.email_account.setReadOnly(True) # Email chỉ đọc
            
            pe = self.dialog.email_account.palette()
            pe.setColor(QPalette.Normal, QPalette.Text, Qt.black)
            pe.setColor(QPalette.Disabled, QPalette.Text, Qt.black)
            pe.setColor(QPalette.Inactive, QPalette.Text, Qt.black)
            self.dialog.email_account.setPalette(pe)
        else:
            # Nếu là Admin, load danh sách tất cả các tài khoản
            try:
                accounts = loans_model.get_accounts()
                self.dialog.user_borrow.clear()
                self.dialog.user_borrow.addItem("", None)
                for acc in accounts:
                    self.dialog.user_borrow.addItem(acc['name'], acc)
            except Exception as e:
                print(f"Lỗi load accounts: {e}")

            self.dialog.user_borrow.setEnabled(True)
            self.dialog.user_borrow.setEditText("")
            self.dialog.user_borrow.setCurrentIndex(0)
            self.dialog.email_account.setText("")
            self.dialog.email_account.setReadOnly(False)
        self.dialog.list_book_borrow.clear()
        self.dialog.search_book_borrow.setText("")
        self.dialog.note_loans.setText("")
        self.dialog.borrow_date.setDate(datetime.now())
        self.dialog.return_date.setDate(datetime.now())
        
        self.refresh_borrow_table_dialog()
        self.dialog.exec_()

    def _on_borrower_changed(self, index):
        data = self.dialog.user_borrow.itemData(index)
        if data:
            self.dialog.email_account.setText(data.get('email', ''))
        else:
            pass

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

    def _get_filter_account_id(self):
        user = getattr(self.main_window, '_current_user', None)
        role = str(user.get('role') or '').lower() if user else None
        if not user or role == 'admin':
            return None
        return user.get('id')

    def refresh_return_table(self):
        try:
            account_id = self._get_filter_account_id()
            rows = loans_model.list_borrowing(account_id)
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Lỗi: {str(e)}")
            print("ERROR:", e)
            return
        
        t = self.screen.table_loans_return
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(row.get("account_name") or ""))
            t.setItem(r, 3, QTableWidgetItem(row["borrow_date"].strftime("%d/%m/%Y")))
            t.setItem(r, 4, QTableWidgetItem(row["due_date"].strftime("%d/%m/%Y")))
            t.setItem(r, 5, QTableWidgetItem(self._format_loan_status(row.get("status"))))


    def _format_loan_status(self, status):
        if status == 'borrowed':
            return 'Đang mượn'
        if status == 'returned':
            return 'Đã trả'
        if status == 'pending':
            return 'Chờ duyệt'
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
        search_text = self.screen.search_book_return.text().strip().lower()
        filter_status = self.screen.combo_filter_status.currentText()
        filter_borrower = self.screen.combo_filter_borrower.currentText()
        filter_date = self.screen.combo_filter_date.currentText()

        try:
            account_id = self._get_filter_account_id()
            rows = loans_model.list_borrowing(account_id)
            filtered_rows = []
            
            for row in rows:
                status_display = self._format_loan_status(row.get("status"))
                match_status = (filter_status == "Tất cả" or status_display == filter_status)
                
                match_borrower = (filter_borrower == "Tất cả" or row.get("account_name") == filter_borrower)
                
                match_date = (filter_date == "Tất cả" or str(row["borrow_date"]) == filter_date)
                match_search = (not search_text or 
                                search_text in row.get('title', '').lower() or 
                                search_text in (row.get('account_name') or "").lower())
                
                if match_search and match_status and match_borrower and match_date:
                    filtered_rows.append(row)
            
            self._display_borrowing_rows(filtered_rows)
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi tải danh sách: {str(e)}")

    def _display_borrowing_rows(self, rows):
        t = self.screen.table_loans_return
        t.setRowCount(len(rows))
        print(rows)
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(row.get("account_name") or ""))
            t.setItem(r, 3, QTableWidgetItem(row["borrow_date"].strftime("%d/%m/%Y")))
            print(row["borrow_date"])
            t.setItem(r, 4, QTableWidgetItem(row["due_date"].strftime("%d/%m/%Y")))
            t.setItem(r, 5, QTableWidgetItem(self._format_loan_status(row.get("status"))))

    def _populate_filter_combos(self):
        try:
            account_id = self._get_filter_account_id()
            rows = loans_model.list_borrowing(account_id)
            
            # Lưu lại selection hiện tại nếu có
            current_borrower = self.screen.combo_filter_borrower.currentText()
            current_date = self.screen.combo_filter_date.currentText()
            
            # Ngắt kết nối tạm thời để tránh loop
            self.screen.combo_filter_borrower.blockSignals(True)
            self.screen.combo_filter_date.blockSignals(True)
            
            # Người mượn
            user = getattr(self.main_window, '_current_user', None)
            role = str(user.get('role') or '').lower() if user else None
            if role == 'admin': # Admin
                all_accounts = loans_model.get_accounts()
                borrowers = sorted([acc['name'] for acc in all_accounts if acc.get('name')])
            else: # Reader
                borrowers = sorted(list(set(row.get("account_name", "") for row in rows if row.get("account_name"))))
            
            self.screen.combo_filter_borrower.clear()
            self.screen.combo_filter_borrower.addItem("Tất cả")
            self.screen.combo_filter_borrower.addItems(borrowers)
            
            # Ngày mượn
            dates = sorted(list(set(str(row["borrow_date"]) for row in rows if row.get("borrow_date"))), reverse=True)
            self.screen.combo_filter_date.clear()
            self.screen.combo_filter_date.addItem("Tất cả")
            self.screen.combo_filter_date.addItems(dates)
            
            idx_b = self.screen.combo_filter_borrower.findText(current_borrower)
            if idx_b >= 0: self.screen.combo_filter_borrower.setCurrentIndex(idx_b)
            
            idx_d = self.screen.combo_filter_date.findText(current_date)
            if idx_d >= 0: self.screen.combo_filter_date.setCurrentIndex(idx_d)
            
            self.screen.combo_filter_borrower.blockSignals(False)
            self.screen.combo_filter_date.blockSignals(False)
            
        except Exception as e:
            print(f"Lỗi populate filters: {e}")

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

    def approve_loan_action(self):
        selected_rows = self.screen.table_loans_return.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.main_window, "Thông báo", "Vui lòng chọn đơn mượn để duyệt!")
            return
        
        row_idx = selected_rows[0].row()
        loan_id = int(self.screen.table_loans_return.item(row_idx, 0).text())
        book_title = self.screen.table_loans_return.item(row_idx, 1).text()
        status_text = self.screen.table_loans_return.item(row_idx, 5).text()

        if status_text != 'Chờ duyệt':
            QMessageBox.warning(self.main_window, "Thông báo", "Chỉ có thể duyệt các đơn ở trạng thái 'Chờ duyệt'!")
            return

        try:
            if loans_model.approve_loan(loan_id):
                QMessageBox.information(self.main_window, "Thành công", f"Đã duyệt mượn sách '{book_title}'!")
                self.refresh_return_table()
            else:
                QMessageBox.warning(self.main_window, "Thất bại", "Không thể duyệt đơn này.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Lỗi khi duyệt: {str(e)}")
            
    def borrow_book_action(self):
        list_widget = self.dialog.list_book_borrow
        if list_widget.count() == 0:
            QMessageBox.warning(self.main_window, "Thông báo", "Vui lòng chọn sách và bấm 'Thêm Sách' vào danh sách mượn!")
            return
            
        user_name = self.dialog.user_borrow.currentText().strip()
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
                error_msg = str(e)
                if "Duplicate entry" in error_msg and "email" in error_msg:
                    QMessageBox.warning(self.main_window, "Lỗi", "Email này đã tồn tại trong hệ thống!")
                else:
                    QMessageBox.critical(self.main_window, "Lỗi", f"Không thể tạo tài khoản mới: {error_msg}")
                return
            
        due_date = self.dialog.return_date.date().toString("yyyy-MM-dd")
        
        # Xác định status dựa trên role
        current_role = self.main_window._current_user.get('role') if hasattr(self.main_window, '_current_user') else 'reader'
        loan_status = 'borrowed' if current_role == 'admin' else 'pending'

        success_count = 0
        try:
            for i in range(list_widget.count()):
                item_text = list_widget.item(i).text()
                book_id = int(item_text.split(" - ")[0])
                loans_model.borrow_book(book_id, account_id, due_date, status=loan_status)
                success_count += 1
            
            msg = f"Đã gửi yêu cầu mượn {success_count} quyển sách!" if loan_status == 'pending' else f"Đã mượn thành công {success_count} quyển sách!"
            QMessageBox.information(self.main_window, "Thành công", msg)
            self.dialog.accept()
            self.refresh_return_table()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi", f"Có lỗi xảy ra. Chi tiết: {e}")

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
