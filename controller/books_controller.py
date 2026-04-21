import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

import pymysql
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog

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
        self._loaded_cover_path = None

        self._add_cover_source_path = None
        self._add_cover_cleared = False
        self._edit_cover_source_path = None
        self._edit_cover_cleared = False

        self._app_dir = Path(__file__).resolve().parent.parent
        self._covers_dir = self._app_dir / "assets" / "book_covers"
        self._covers_dir.mkdir(parents=True, exist_ok=True)

        self._screen.btn_book_save.clicked.connect(self._on_save_new)
        self._screen.btn_search_book.clicked.connect(self._on_search)
        self._screen.btn_edit_save.clicked.connect(self._on_update)
        self._screen.btn_edit_delete.clicked.connect(self._on_delete)
        self._screen.btn_books_refresh.clicked.connect(self.refresh_book_table)
        self._screen.btn_books_load_edit.clicked.connect(self._load_selection_to_edit)
        self._screen.btn_books_delete.clicked.connect(self._delete_selected_row)

        if hasattr(self._screen, "btn_choose_cover_add"):
            self._screen.btn_choose_cover_add.clicked.connect(self._on_choose_cover_add)
        if hasattr(self._screen, "btn_clear_cover_add"):
            self._screen.btn_clear_cover_add.clicked.connect(self._on_clear_cover_add)
        if hasattr(self._screen, "btn_choose_cover_edit"):
            self._screen.btn_choose_cover_edit.clicked.connect(self._on_choose_cover_edit)
        if hasattr(self._screen, "btn_clear_cover_edit"):
            self._screen.btn_clear_cover_edit.clicked.connect(self._on_clear_cover_edit)

        self.refresh_comboboxes()
        self.refresh_book_table()
        self._set_cover_preview_add(None)
        self._set_cover_preview_edit(None)

    def _set_cover_preview(self, label, absolute_image_path: Optional[Path]):
        if not label:
            return
        if not absolute_image_path or not absolute_image_path.is_file():
            label.setPixmap(QPixmap())
            label.setText(self._main.tr("Chưa có ảnh"))
            return
        pix = QPixmap(str(absolute_image_path))
        if pix.isNull():
            label.setPixmap(QPixmap())
            label.setText(self._main.tr("Không thể tải ảnh"))
            return
        scaled = pix.scaled(
            label.width(),
            label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        label.setPixmap(scaled)
        label.setText("")

    def _set_cover_preview_add(self, cover_path_relative: Optional[str]):
        label = getattr(self._screen, "label_cover_preview_add", None)
        abs_path = None
        if cover_path_relative:
            abs_path = (self._app_dir / cover_path_relative).resolve()
        self._set_cover_preview(label, abs_path)

    def _set_cover_preview_edit(self, cover_path_relative: Optional[str]):
        label = getattr(self._screen, "label_cover_preview_edit", None)
        abs_path = None
        if cover_path_relative:
            abs_path = (self._app_dir / cover_path_relative).resolve()
        self._set_cover_preview(label, abs_path)

    def _pick_image_file(self) -> Optional[str]:
        file_path, _ = QFileDialog.getOpenFileName(
            self._main,
            self._main.tr("Chọn ảnh bìa"),
            "",
            self._main.tr("Images (*.png *.jpg *.jpeg *.webp);;All files (*)"),
        )
        return file_path or None

    def _copy_cover_to_assets(self, source_path: str) -> str:
        src = Path(source_path)
        ext = src.suffix.lower() if src.suffix else ".png"
        file_name = f"{uuid4().hex}{ext}"
        dest = self._covers_dir / file_name
        shutil.copy2(str(src), str(dest))
        return str(Path("assets") / "book_covers" / file_name)

#chọn ảnh mới
    def _on_choose_cover_add(self):
        p = self._pick_image_file()
        if not p:
            return
        self._add_cover_source_path = p
        self._add_cover_cleared = False
        self._set_cover_preview(getattr(self._screen, "label_cover_preview_add", None), Path(p))

    def _on_clear_cover_add(self):
        self._add_cover_source_path = None
        self._add_cover_cleared = True
        self._set_cover_preview_add(None)

    def _on_choose_cover_edit(self):
        p = self._pick_image_file()
        if not p:
            return
        self._edit_cover_source_path = p
        self._edit_cover_cleared = False
        self._set_cover_preview(getattr(self._screen, "label_cover_preview_edit", None), Path(p))

    def _on_clear_cover_edit(self):
        self._edit_cover_source_path = None
        self._edit_cover_cleared = True
        self._loaded_cover_path = None
        self._set_cover_preview_edit(None)

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
        self._loaded_cover_path = row.get("cover_path")
        self._screen.edit_search_title.setText(row["title"])
        self._screen.edit_edit_title.setText(row["title"])
        self._screen.edit_edit_code.setText(row["code"])
        self._screen.edit_edit_quantity.setText(str(row["quantity"]))
        self._screen.edit_edit_year.setText(str(row["year"]))
        self._screen.edit_edit_description.setPlainText(row["description"] or "")
        set_combo_current_data(self._screen.combo_edit_category, row["category_id"])
        set_combo_current_data(self._screen.combo_edit_author, row["author_id"])
        set_combo_current_data(self._screen.combo_edit_publisher, row["publisher_id"])
        self._edit_cover_source_path = None
        self._edit_cover_cleared = False
        self._set_cover_preview_edit(self._loaded_cover_path)
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
            self._main.tr("Xác nhận xóa"),
            self._main.tr("Bạn có chắc chắn muốn xóa sách này?"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                book_model.delete_by_id(bid)
            except pymysql.Error:
                self._main.statusBar().showMessage(self._main.tr("Không thể xóa sách."))
                return
        if self._loaded_book_id == bid:
            self._loaded_book_id = None
        self.refresh_book_table()
        self._main.statusBar().showMessage(self._main.tr("Sách đã được xoá."))
        
    def _on_save_new(self):
        title = self._screen.edit_book_title.text()
        code = self._screen.edit_book_code.text()
        if not title.strip() or not code.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Vui lòng nhập tên sách và mã sách.")
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
                self._main.tr("Vui lòng chọn danh mục, tác giả và nhà xuất bản.")
            )
            return
        cover_path = None
        if self._add_cover_source_path and not self._add_cover_cleared:
            try:
                cover_path = self._copy_cover_to_assets(self._add_cover_source_path)
            except Exception:
                self._main.statusBar().showMessage(self._main.tr("Không thể lưu ảnh bìa."))
                return
        try:
            book_model.insert_book(
                title,
                code,
                qty,
                year,
                desc,
                int(cid),
                int(aid),
                int(pid),
                cover_path=cover_path,
            )
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Không thể thêm sách: {0}").format(e.args[0])
            )
            return

        self._main.statusBar().showMessage(self._main.tr("Sách đã được thêm."))
        self._screen.edit_book_title.clear()
        self._screen.edit_book_code.clear()
        self._screen.edit_book_quantity.clear()
        self._screen.edit_book_year.clear()
        self._screen.edit_book_description.clear()
        self._add_cover_source_path = None
        self._add_cover_cleared = False
        self._set_cover_preview_add(None)
        self.refresh_book_table()

    def _on_search(self):
        title = self._screen.edit_search_title.text()
        if not title.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Vui lòng nhập tên sách cần tìm.")
            )
            return
        try:
            row = book_model.find_by_title(title)
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Không thể tìm thấy sách.")
            )
            return
        if not row:
            self._loaded_book_id = None
            self._main.statusBar().showMessage(self._main.tr("Không tìm thấy sách."))
            return
        self._loaded_book_id = row["id"]
        self._loaded_cover_path = row.get("cover_path")
        self._screen.edit_edit_title.setText(row["title"])
        self._screen.edit_edit_code.setText(row["code"])
        self._screen.edit_edit_quantity.setText(str(row["quantity"]))
        self._screen.edit_edit_year.setText(str(row["year"]))
        self._screen.edit_edit_description.setPlainText(row["description"] or "")
        set_combo_current_data(self._screen.combo_edit_category, row["category_id"])
        set_combo_current_data(self._screen.combo_edit_author, row["author_id"])
        set_combo_current_data(self._screen.combo_edit_publisher, row["publisher_id"])
        self._edit_cover_source_path = None
        self._edit_cover_cleared = False
        self._set_cover_preview_edit(self._loaded_cover_path)
        self._main.statusBar().showMessage(self._main.tr("Sách đã được tải."))
        self._screen.tabWidget_books.setCurrentIndex(self.TAB_EDIT)

    def _on_update(self):
        if self._loaded_book_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Vui lòng tìm hoặc tải một cuốn sách trước khi lưu thay đổi.")
            )
            return
        title = self._screen.edit_edit_title.text()
        code = self._screen.edit_edit_code.text()
        if not title.strip() or not code.strip():
            self._main.statusBar().showMessage(
                self._main.tr("Vui lòng nhập tên sách và mã sách.")
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
                self._main.tr("Vui lòng chọn danh mục, tác giả và nhà xuất bản.")
            )
            return
        cover_path = self._loaded_cover_path
        if self._edit_cover_cleared:
            cover_path = None
        elif self._edit_cover_source_path:
            try:
                cover_path = self._copy_cover_to_assets(self._edit_cover_source_path)
            except Exception:
                self._main.statusBar().showMessage(self._main.tr("Không thể lưu ảnh bìa."))
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
                cover_path=cover_path,
            )
        except pymysql.Error as e:
            self._main.statusBar().showMessage(
                self._main.tr("Không thể cập nhật sách: {0}").format(e.args[0])
            )
            return
        self._loaded_cover_path = cover_path
        self._edit_cover_source_path = None
        self._edit_cover_cleared = False
        self._set_cover_preview_edit(self._loaded_cover_path)
        self._main.statusBar().showMessage(self._main.tr("Sách đã được cập nhật."))
        self.refresh_book_table()

    def _on_delete(self):
        if self._loaded_book_id is None:
            self._main.statusBar().showMessage(
                self._main.tr("Vui lòng tải một cuốn sách trước khi xóa.")
            )
            return
        reply = QMessageBox.question(
            self._main,
            self._main.tr("Xác nhận xóa"),
            self._main.tr("Bạn có chắc chắn muốn xóa sách này?"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                book_model.delete_by_id(self._loaded_book_id)
            except pymysql.Error:
                self._main.statusBar().showMessage(self._main.tr("Không thể xóa sách."))
                return
        self._loaded_book_id = None
        self._loaded_cover_path = None
        self._edit_cover_source_path = None
        self._edit_cover_cleared = False
        self._screen.edit_edit_title.clear()
        self._screen.edit_edit_code.clear()
        self._screen.edit_edit_quantity.clear()
        self._screen.edit_edit_year.clear()
        self._screen.edit_edit_description.clear()
        self._screen.edit_search_title.clear()
        self._set_cover_preview_edit(None)
        self._main.statusBar().showMessage(self._main.tr("Sách đã được xóa."))
        self.refresh_book_table()
