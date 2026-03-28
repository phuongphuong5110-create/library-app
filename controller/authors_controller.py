import pymysql
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

from model import author_model


class AuthorsController:
    def __init__(self, main_window: QMainWindow, screen):
        self._main = main_window
        self._screen = screen
        self._selected_id = None

        self._screen.btn_author_add.clicked.connect(self._add)
        self._screen.btn_author_update.clicked.connect(self._update)
        self._screen.btn_author_delete.clicked.connect(self._delete)
        self._screen.btn_author_clear.clicked.connect(self._clear)
        self._screen.table_authors.itemSelectionChanged.connect(
            self._on_selection_changed
        )

        self.refresh_table()

    def refresh_table(self):
        try:
            rows = author_model.list_rows()
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not load authors (database error).")
            )
            return
        t = self._screen.table_authors
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            id_item = QTableWidgetItem(str(row["id"]))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            t.setItem(r, 0, id_item)
            name_item = QTableWidgetItem(row["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            t.setItem(r, 1, name_item)

    def _on_selection_changed(self):
        rows = self._screen.table_authors.selectionModel().selectedRows()
        if not rows:
            self._selected_id = None
            return
        r = rows[0].row()
        id_item = self._screen.table_authors.item(r, 0)
        name_item = self._screen.table_authors.item(r, 1)
        if not id_item or not name_item:
            return
        try:
            self._selected_id = int(id_item.text())
        except ValueError:
            self._selected_id = None
            return
        self._screen.edit_author_name.setText(name_item.text())

    def _add(self):
        name = self._screen.edit_author_name.text()
        if not name.strip():
            self._main.statusBar().showMessage(self._main.tr("Enter an author name."))
            return
        try:
            author_model.insert(name)
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Could not add author: {0}").format(e.args[0])
            )
            return
        self._main.statusBar().showMessage(self._main.tr("Author added."))
        self._clear()
        self.refresh_table()

    def _update(self):
        name = self._screen.edit_author_name.text()
        if not name.strip():
            self._main.statusBar().showMessage(self._main.tr("Enter an author name."))
            return
        if self._selected_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Select a row to update.")
            )
            return
        try:
            author_model.update_row(self._selected_id, name)
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Could not update author: {0}").format(e.args[0])
            )
            return
        self._main.statusBar().showMessage(self._main.tr("Author updated."))
        self.refresh_table()

    def _delete(self):
        if self._selected_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Select a row to delete.")
            )
            return
        reply = QMessageBox.question(
            self._main,
            self._main.tr("Confirm delete"),
            self._main.tr("Delete this author?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            author_model.delete_by_id(self._selected_id)
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Could not delete: {0}").format(e.args[0])
            )
            return
        self._main.statusBar().showMessage(self._main.tr("Author deleted."))
        self._clear()
        self.refresh_table()

    def _clear(self):
        self._selected_id = None
        self._screen.edit_author_name.clear()
        self._screen.table_authors.clearSelection()
