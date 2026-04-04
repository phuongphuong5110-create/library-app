from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QWidget

from controller.authors_controller import AuthorsController
from controller.books_controller import BooksController
from controller.categories_controller import CategoriesController
from controller.publishers_controller import PublishersController
from controller.stats_controller import StatsController
from controller.accounts_controller import AccountsController

_VIEW_DIR = Path(__file__).resolve().parent.parent / "view"

_SCREEN_FILES = (
    "screen_stats.ui",
    "screen_books.ui",
    "screen_categories.ui",
    "screen_authors.ui",
    "screen_publishers.ui",
    "screen_accounts.ui",
)


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(_VIEW_DIR / "main_window.ui"), self)

        self._stats_ctrl = None
        self._books_ctrl = None
        self._categories_ctrl = None
        self._authors_ctrl = None
        self._publishers_ctrl = None
        self._accounts_ctrl = None

        self._load_screens()

        self.btn_nav_stats.clicked.connect(lambda: self._go(0))
        self.btn_nav_books.clicked.connect(lambda: self._go(1))
        self.btn_nav_categories.clicked.connect(lambda: self._go(2))
        self.btn_nav_authors.clicked.connect(lambda: self._go(3))
        self.btn_nav_publishers.clicked.connect(lambda: self._go(4))
        self.btn_nav_accounts.clicked.connect(lambda: self._go(5))

    def _load_screens(self):
        stack = self.stacked_screens
        for name in _SCREEN_FILES:
            w = QWidget()
            uic.loadUi(str(_VIEW_DIR / name), w)
            stack.addWidget(w)

        self._stats_ctrl = StatsController(self, stack.widget(0))
        self._books_ctrl = BooksController(self, stack.widget(1))
        self._categories_ctrl = CategoriesController(self, stack.widget(2))
        self._authors_ctrl = AuthorsController(self, stack.widget(3))
        self._publishers_ctrl = PublishersController(self, stack.widget(4))
        self._accounts_ctrl = AccountsController(self, stack.widget(5))

    def _go(self, index):
        # Hiển thị screen tương ứng
        self.stacked_screens.setCurrentIndex(index)
        if index == 0 and self._stats_ctrl:
            self._stats_ctrl.refresh_all()
        if index == 1 and self._books_ctrl:
            self._books_ctrl.refresh_comboboxes()
            self._books_ctrl.refresh_book_table()
        if index == 2 and self._categories_ctrl:
            self._categories_ctrl.refresh_table()
        if index == 3 and self._authors_ctrl:
            self._authors_ctrl.refresh_table()
        if index == 4 and self._publishers_ctrl:
            self._publishers_ctrl.refresh_table()
        if index == 5 and self._accounts_ctrl:
            self._accounts_ctrl.refresh_table()
        
