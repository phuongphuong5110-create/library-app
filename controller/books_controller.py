import pymysql
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

from controller.combo_utils import fill_combobox_with_ids, set_combo_current_data
from model import author_model, book_model, category_model, publisher_model


def _parse_int(text, default=0):
    text = (text or "").strip()
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


class BooksController:
    TAB_LIST = 0
    TAB_ADD = 1
    TAB_EDIT = 2

    def __init__(self, main_window: QMainWindow, screen):
        self._main = main_window
        self._screen = screen
        self._loaded_book_id = None

        self._screen.btn_book_save.clicked.connect(self._on_save_new)
        self._screen.btn_search_book.clicked.connect(self._on_search)
        self._screen.btn_edit_save.clicked.connect(self._on_update)
        self._screen.btn_edit_delete.clicked.connect(self._on_delete)
        self._screen.btn_books_refresh.clicked.connect(self.refresh_book_table)
        self._screen.btn_books_load_edit.clicked.connect(self._load_selection_to_edit)
        self._screen.btn_books_delete.clicked.connect(self._delete_selected_row)

        self.refresh_comboboxes()
        self.refresh_book_table()

    def refresh_comboboxes(self):
        try:
            cats = category_model.names_for_combobox()
            authors = author_model.names_for_combobox()
            pubs = publisher_model.names_for_combobox()
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not load lists (database error).")
            )
            return

        for combo in (
            self._screen.combo_book_category,
            self._screen.combo_edit_category,
        ):
            fill_combobox_with_ids(combo, cats)
        for combo in (
            self._screen.combo_book_author,
            self._screen.combo_edit_author,
        ):
            fill_combobox_with_ids(combo, authors)
        for combo in (
            self._screen.combo_book_publisher,
            self._screen.combo_edit_publisher,
        ):
            fill_combobox_with_ids(combo, pubs)

    def refresh_book_table(self):
        try:
            rows = book_model.list_for_stats_table()
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not load books (database error).")
            )
            return
        t = self._screen.table_books
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            t.setItem(r, 1, QTableWidgetItem(row["title"]))
            t.setItem(r, 2, QTableWidgetItem(row["code"]))
            t.setItem(r, 3, QTableWidgetItem(str(row["quantity"])))
            t.setItem(r, 4, QTableWidgetItem(str(row["year"])))
            t.setItem(r, 5, QTableWidgetItem(row["category_name"]))
            t.setItem(r, 6, QTableWidgetItem(row["author_name"]))
            t.setItem(r, 7, QTableWidgetItem(row["publisher_name"]))

    def _selected_book_id(self):
        rows = self._screen.table_books.selectionModel().selectedRows()
        if not rows:
            return None
        r = rows[0].row()
        item = self._screen.table_books.item(r, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    def _load_selection_to_edit(self):
        bid = self._selected_book_id()
        if bid is None:
            self._main.statusBar().showMessage(
                self._main.tr("Select a book in the table first.")
            )
            return
        self._load_book_id_into_form(bid)
        self._screen.tabWidget_books.setCurrentIndex(self.TAB_EDIT)

    def _load_book_id_into_form(self, book_id):
        try:
            row = book_model.find_by_id(book_id)
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not load book (database error).")
            )
            return
        if not row:
            self._loaded_book_id = None
            self._main.statusBar().showMessage(self._main.tr("Book not found."))
            return
        self._loaded_book_id = row["id"]
        self._screen.edit_search_title.setText(row["title"])
        self._screen.edit_edit_title.setText(row["title"])
        self._screen.edit_edit_code.setText(row["code"])
        self._screen.edit_edit_quantity.setText(str(row["quantity"]))
        self._screen.edit_edit_year.setText(str(row["year"]))
        self._screen.edit_edit_description.setPlainText(row["description"] or "")
        set_combo_current_data(self._screen.combo_edit_category, row["category_id"])
        set_combo_current_data(self._screen.combo_edit_author, row["author_id"])
        set_combo_current_data(self._screen.combo_edit_publisher, row["publisher_id"])
        self._main.statusBar().showMessage(self._main.tr("Book loaded."))

    def _delete_selected_row(self):
        bid = self._selected_book_id()
        if bid is None:
            self._main.statusBar().showMessage(
                self._main.tr("Select a book in the table first.")
            )
            return
        reply = QMessageBox.question(
            self._main,
            self._main.tr("Confirm delete"),
            self._main.tr("Delete this book permanently?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            book_model.delete_by_id(bid)
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not delete book.")
            )
            return
        if self._loaded_book_id == bid:
            self._loaded_book_id = None
        self.refresh_book_table()
        self._main.statusBar().showMessage(self._main.tr("Book deleted."))

    def _on_save_new(self):
        title = self._screen.edit_book_title.text()
        code = self._screen.edit_book_code.text()
        if not title.strip() or not code.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Title and code are required.")
            )
            return
        qty = _parse_int(self._screen.edit_book_quantity.text(), 0)
        year = _parse_int(self._screen.edit_book_year.text(), 0)
        desc = self._screen.edit_book_description.toPlainText()
        cid = self._screen.combo_book_category.currentData()
        aid = self._screen.combo_book_author.currentData()
        pid = self._screen.combo_book_publisher.currentData()
        if cid is None or aid is None or pid is None:
            self._main.statusBar().showMessage(
                self._main.tr("Please select category, author, and publisher.")
            )
            return
        try:
            book_model.insert_book(
                title, code, qty, year, desc, int(cid), int(aid), int(pid)
            )
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Could not save book: {0}").format(e.args[0])
            )
            return

        self._main.statusBar().showMessage(self._main.tr("New book added."))
        self._screen.edit_book_title.clear()
        self._screen.edit_book_code.clear()
        self._screen.edit_book_quantity.clear()
        self._screen.edit_book_year.clear()
        self._screen.edit_book_description.clear()
        self.refresh_book_table()

    def _on_search(self):
        title = self._screen.edit_search_title.text()
        if not title.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Enter a book title to search.")
            )
            return
        try:
            row = book_model.find_by_title(title)
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Search failed (database error).")
            )
            return
        if not row:
            self._loaded_book_id = None
            self._main.statusBar().showMessage(self._main.tr("No book found."))
            return
        self._loaded_book_id = row["id"]
        self._screen.edit_edit_title.setText(row["title"])
        self._screen.edit_edit_code.setText(row["code"])
        self._screen.edit_edit_quantity.setText(str(row["quantity"]))
        self._screen.edit_edit_year.setText(str(row["year"]))
        self._screen.edit_edit_description.setPlainText(row["description"] or "")
        set_combo_current_data(self._screen.combo_edit_category, row["category_id"])
        set_combo_current_data(self._screen.combo_edit_author, row["author_id"])
        set_combo_current_data(self._screen.combo_edit_publisher, row["publisher_id"])
        self._main.statusBar().showMessage(self._main.tr("Book loaded."))

    def _on_update(self):
        if self._loaded_book_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Search or load a book before saving changes.")
            )
            return
        title = self._screen.edit_edit_title.text()
        code = self._screen.edit_edit_code.text()
        if not title.strip() or not code.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Title and code are required.")
            )
            return
        qty = _parse_int(self._screen.edit_edit_quantity.text(), 0)
        year = _parse_int(self._screen.edit_edit_year.text(), 0)
        desc = self._screen.edit_edit_description.toPlainText()
        cid = self._screen.combo_edit_category.currentData()
        aid = self._screen.combo_edit_author.currentData()
        pid = self._screen.combo_edit_publisher.currentData()
        if cid is None or aid is None or pid is None:
            self._main.statusBar().showMessage(
                self._main.tr("Please select category, author, and publisher.")
            )
            return
        try:
            book_model.update_book(
                self._loaded_book_id,
                title,
                code,
                qty,
                year,
                desc,
                int(cid),
                int(aid),
                int(pid),
            )
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Could not update book: {0}").format(e.args[0])
            )
            return
        self._main.statusBar().showMessage(self._main.tr("Book updated."))
        self.refresh_book_table()

    def _on_delete(self):
        if self._loaded_book_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Load a book before deleting.")
            )
            return
        reply = QMessageBox.question(
            self._main,
            self._main.tr("Confirm delete"),
            self._main.tr("Delete this book permanently?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            book_model.delete_by_id(self._loaded_book_id)
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not delete book.")
            )
            return
        self._loaded_book_id = None
        self._screen.edit_edit_title.clear()
        self._screen.edit_edit_code.clear()
        self._screen.edit_edit_quantity.clear()
        self._screen.edit_edit_year.clear()
        self._screen.edit_edit_description.clear()
        self._screen.edit_search_title.clear()
        self._main.statusBar().showMessage(self._main.tr("Book deleted."))
        self.refresh_book_table()
