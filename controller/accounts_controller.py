import pymysql
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt

from controller.combo_utils import fill_combobox_with_ids, set_combo_current_data
from model import author_model, book_model, category_model, publisher_model, account_model


def _parse_int(text, default=0):
    text = (text or "").strip()
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


class AccountsController:
    TAB_LIST = 0
    TAB_ADD = 1
    TAB_EDIT = 2

    def __init__(self, main_window: QMainWindow, screen, current_user):
        self._main = main_window
        self._screen = screen
        self._current_user = current_user
        
        self._screen.btn_reader_add.clicked.connect(self._on_add)
        self._screen.btn_reader_edit.clicked.connect(self._on_edit)
        self._screen.btn_reader_delete.clicked.connect(self._on_delete)
        self._screen.btn_reader_save.clicked.connect(self._on_save)
        self._screen.btn_reader_delete_2.clicked.connect(self._on_cancel)
        
        self._screen.tableWidget.itemSelectionChanged.connect(
            self._on_selection_changed
        )
        self._screen.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self._loaded_account_id = None
        self._screen.tabWidget.setCurrentIndex(0)
        self.refresh_table()
        
    def _on_add(self):
        self._loaded_account_id = None
        self._screen.edit_reader_name.clear()
        self._screen.edit_email_name.clear()
        self._screen.comboBox_role.setCurrentIndex(0)
        self._screen.tabWidget.setCurrentIndex(1)
        self._screen.edit_reader_name.setFocus()
    
    def _on_edit(self):
        if self._loaded_account_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Vui lòng chọn một tài khoản trong bảng.")
            )
            return
        self._screen.tabWidget.setCurrentIndex(1)
        self._screen.edit_reader_name.setFocus()
    
    def _on_cancel(self):
        self._loaded_account_id = None
        self._screen.edit_reader_name.clear()
        self._screen.edit_email_name.clear()
        self._screen.comboBox_role.setCurrentIndex(0)
        self._screen.tabWidget.setCurrentIndex(0)
    
    def _on_save(self):
        name = self._screen.edit_reader_name.text().strip()
        email = self._screen.edit_email_name.text().strip()
        role = self._screen.comboBox_role.currentText()
        
        if not name or not email:
            QMessageBox.warning(self._main, "Cảnh báo", "Vui lòng điền đầy đủ thông tin")
            return
        
        try:
            if self._loaded_account_id:
                account_model.update_account(self._loaded_account_id, name, email, role)
            else:
                account_model.create_account(name, email, role)
            
            self._on_cancel()
            self.refresh_table()
        except pymysql.Error as e:
            QMessageBox.critical(self._main, "Lỗi", str(e))

    def refresh_table(self):
        try:
            rows = account_model.list_all_accounts()
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not load accounts (database error).")
            )
            return
        
        table = self._screen.tableWidget
        table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            table.setItem(row_idx, 0, QTableWidgetItem(str(row['id'])))
            table.setItem(row_idx, 1, QTableWidgetItem(row['name']))
            table.setItem(row_idx, 2, QTableWidgetItem(row['email']))
            table.setItem(row_idx, 3, QTableWidgetItem(row['role']))
            for col in range(4):
                item = table.item(row_idx, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def _selected_account_id(self):
        r = self._screen.tableWidget.currentRow()
        if r < 0:
            return None
        item = self._screen.tableWidget.item(r, 0)
        print(item)
        if not item:
            return None
        try:
            print(item.text())
            return int(item.text())
        except ValueError:
            return None

    def _on_selection_changed(self):
        account_id = self._selected_account_id()
        if account_id is None:
            self._loaded_account_id = None
            return
        try:
            row = account_model.find_by_id(account_id)
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not load account (database error).")
            )
            return
        if not row:
            self._loaded_account_id = None
            self._main.statusBar().showMessage(self._main.tr("Account not found."))
            return
        self._loaded_account_id = row["id"]
        self._screen.edit_reader_name.setText(row["name"])
        self._screen.edit_email_name.setText(row["email"])
        # Set role combobox
        index = self._screen.comboBox_role.findText(row["role"])
        if index >= 0:
            self._screen.comboBox_role.setCurrentIndex(index)
    
    def _on_delete(self):
        account_id = self._selected_account_id()
        if account_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Vui lòng chọn một tài khoản trong bảng.")
            )
            return

        # Kiểm tra quyền admin
        if not self._current_user or self._current_user.get('role') != 'admin':
            QMessageBox.warning(self._main, "Lỗi", "Chỉ admin mới có quyền xóa tài khoản!")
            return
        
        # Lấy thông tin tài khoản để kiểm tra role
        try:
            account = account_model.find_by_id(account_id)
            if not account:
                self._main.statusBar().showMessage("Tài khoản không tồn tại.")
                return
            # Admin có thể xóa tất cả
        except pymysql.Error as e:
            QMessageBox.critical(self._main, "Lỗi", f"Không thể kiểm tra tài khoản: {str(e)}")
            return
        
        msg = QMessageBox(self._main)
        msg.setWindowTitle("Xác nhận xóa")
        msg.setText("Bạn có chắc chắn muốn xóa tài khoản này?")
        
        btn_yes = msg.addButton("Xoá", QMessageBox.YesRole)
        btn_no = msg.addButton("Hủy", QMessageBox.NoRole)
            
        msg.exec_()
        
        if msg.clickedButton() == btn_yes:
            try:
                account_model.delete_by_id(account_id)
                self.refresh_table()
                self._main.statusBar().showMessage("Đã xóa tài khoản thành công.")
            except pymysql.Error as e:
                QMessageBox.critical(self._main, "Lỗi", f"Không thể xóa tài khoản: {str(e)}")

    def is_email_exists(email):
        query = "SELECT 1 FROM users WHERE email = %s LIMIT 1"
        cursor.execute(query, (email,))
        return cursor.fetchone()
    
    def handle_register(self):
        if is_email_exists(self.email):
            QMessageBox.warning(self._main, "Lỗi", "Email đã tồn tại!")
        return

