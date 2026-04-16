import pymysql
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

from model import category_model


class CategoriesController:
    def __init__(self, main_window: QMainWindow, screen):
        self._main = main_window
        self._screen = screen
        self._selected_id = None

        self._screen.btn_category_add.clicked.connect(self._add)
        self._screen.btn_category_update.clicked.connect(self._update)
        self._screen.btn_category_delete.clicked.connect(self._delete)
        self._screen.btn_category_clear.clicked.connect(self._clear)
        self._screen.table_categories.itemSelectionChanged.connect(
            self._on_selection_changed
        )

        self.refresh_table()

    def refresh_table(self):
        try:
            rows = category_model.list_rows()
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Không thể tải danh sách thể loại.")
            )
            return
        t = self._screen.table_categories
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            id_item = QTableWidgetItem(str(row["id"]))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            t.setItem(r, 0, id_item)
            name_item = QTableWidgetItem(row["category_name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            t.setItem(r, 1, name_item)

    def _on_selection_changed(self):
        rows = self._screen.table_categories.selectionModel().selectedRows()
        if not rows:
            self._selected_id = None
            return
        r = rows[0].row()
        id_item = self._screen.table_categories.item(r, 0)
        name_item = self._screen.table_categories.item(r, 1)
        if not id_item or not name_item:
            return
        try:
            self._selected_id = int(id_item.text())
        except ValueError:
            self._selected_id = None
            return
        self._screen.edit_category_name.setText(name_item.text())

    def _add(self):
        name = self._screen.edit_category_name.text()
        if not name.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Nhập tên thể loại.")
            )
            return
        try:
            category_model.insert(name)
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Không thể thêm thể loại: {0}").format(e.args[0])
            )
            return
        self._main.statusBar().showMessage(self._main.tr("Thể loại đã được thêm."))
        self._clear()
        self.refresh_table()

    def _update(self):
        name = self._screen.edit_category_name.text()
        if not name.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Nhập tên thể loại.")
            )
            return
        if self._selected_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Chọn một dòng để cập nhật.")
            )
            return
        try:
            category_model.update_row(self._selected_id, name)
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Không thể cập nhật thể loại: {0}").format(e.args[0])
            )
            return
        self._main.statusBar().showMessage(self._main.tr("Thể loại đã được cập nhật."))
        self.refresh_table()

    def _delete(self):
        if self._selected_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Chọn một dòng để xóa.")
            )
            return
        msg = QMessageBox(self._main)
        msg.setWindowTitle("Xác nhận xóa")
        msg.setText("Bạn có chắc chắn muốn xóa thể loại này?")
        
        btn_yes = msg.addButton("Xoá", QMessageBox.YesRole)
        btn_no = msg.addButton("Hủy", QMessageBox.NoRole)
            
        msg.exec_()
        
        if msg.clickedButton() == btn_yes:
            try:
                category_model.delete_by_id(self._selected_id)
            except pymysql.Error as e:
                self._main.statusBar().showMessage(
                    self._main.tr("Không thể xóa: {0}").format(e.args[0])
                )
                return
        self._main.statusBar().showMessage(self._main.tr("Thể loại đã được xóa."))
        self._clear()
        self.refresh_table()

    def _clear(self):
        self._selected_id = None
        self._screen.edit_category_name.clear()
        self._screen.table_categories.clearSelection()
