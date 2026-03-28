import pymysql
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem

from model import author_model, book_model, category_model, publisher_model


class StatsController:
    def __init__(self, main_window: QMainWindow, screen):
        self._main = main_window
        self._screen = screen
        self.refresh_all()

    def refresh_all(self):
        try:
            nb = book_model.count_all()
            nc = category_model.count_all()
            na = author_model.count_all()
            np = publisher_model.count_all()
            rows = book_model.list_for_stats_table()
        except pymysql.Error:
            self._main.statusBar().showMessage(
                self._main.tr("Could not load dashboard (database error).")
            )
            return

        self._screen.label_stat_books_value.setText(str(nb))
        self._screen.label_stat_categories_value.setText(str(nc))
        self._screen.label_stat_authors_value.setText(str(na))
        self._screen.label_stat_publishers_value.setText(str(np))

        table = self._screen.table_stats_books
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            table.setItem(r, 0, QTableWidgetItem(row["code"]))
            table.setItem(r, 1, QTableWidgetItem(row["title"]))
            table.setItem(r, 2, QTableWidgetItem(str(row["year"])))
            table.setItem(r, 3, QTableWidgetItem(str(row["quantity"])))
            table.setItem(r, 4, QTableWidgetItem(row["category_name"]))
            table.setItem(r, 5, QTableWidgetItem(row["author_name"]))
