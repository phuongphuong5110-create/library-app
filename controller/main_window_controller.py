from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget
from view.login_ui import Ui_mainWindow
from model.db import get_connection
from model.user_model import User

from controller.authors_controller import AuthorsController
from controller.books_controller import BooksController
from controller.categories_controller import CategoriesController
from controller.publishers_controller import PublishersController
from controller.stats_controller import StatsController
from controller.accounts_controller import AccountsController
from controller.loans_controller import LoansController
from controller.users_controller import UsersController

_VIEW_DIR = Path(__file__).resolve().parent.parent / "view"

_SCREEN_FILES = (
    "screen_stats.ui",
    "screen_books.ui",
    "screen_categories.ui",
    "screen_authors.ui",
    "screen_publishers.ui",
    "screen_accounts.ui",
    "screen_loans.ui",
)
class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(_VIEW_DIR / "main_window.ui"), self)
        
        import main
        self._current_user = main.current_user

        self._stats_ctrl = None
        self._books_ctrl = None
        self._categories_ctrl = None
        self._authors_ctrl = None
        self._publishers_ctrl = None
        self._accounts_ctrl = None
        self._loans_ctrl = None

        self._load_screens()

        self.btn_nav_stats.clicked.connect(lambda: self._go(0))
        self.btn_nav_books.clicked.connect(lambda: self._go(1))
        self.btn_nav_categories.clicked.connect(lambda: self._go(2))
        self.btn_nav_authors.clicked.connect(lambda: self._go(3))
        self.btn_nav_publishers.clicked.connect(lambda: self._go(4))
        self.btn_nav_accounts.clicked.connect(lambda: self._go(5))
        self.btn_nav_loans.clicked.connect(lambda: self._go(6))

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
        self._accounts_ctrl = AccountsController(self, stack.widget(5), self._current_user)
        self._loans_ctrl = LoansController(self, stack.widget(6))

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
        if index == 6 and self._loans_ctrl:
            self._loans_ctrl.refresh_borrow_table()
            self._loans_ctrl.refresh_return_table()
            
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        # bắt sự kiện nút login
        self.ui.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()
        con = None
        try:
            con = get_connection()
            user_model = User(con)
            user = user_model.check_admin_login(username, password) or user_model.check_staff_login(username, password)
            if user:
                import main
                main.current_user = user
                self.open_main()
            else:
                QMessageBox.warning(self, "Login Failed", "Sai tên đăng nhập hoặc mật khẩu.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Đã xảy ra lỗi: {str(e)}")
        finally:
            if con:
                con.close()
                
    def setup_permissions(self):
        if self.curent_user_role == 'admin':
            # Admin có quyền truy cập tất cả
            self.ui.btn_nav_stats.setEnabled(True)
            self.ui.btn_nav_books.setEnabled(True)
            self.ui.btn_nav_categories.setEnabled(True)
            self.ui.btn_nav_authors.setEnabled(True)
            self.ui.btn_nav_publishers.setEnabled(True)
            self.ui.btn_nav_accounts.setEnabled(True)
            self.ui.btn_nav_loans.setEnabled(True)
        elif self.current_user_role == 'staff':
            self.tabwidget.removeTab(4)
            self.tabwidget.removeTab(5)
            self.tabwidget.removeTab(2)
        else:
            # Nếu role không xác định, tắt tất cả
            self.ui.btn_nav_stats.setEnabled(False)
            self.ui.btn_nav_books.setEnabled(False)
            self.ui.btn_nav_categories.setEnabled(False)
            self.ui.btn_nav_authors.setEnabled(False)  
            self.ui.btn_nav_publishers.setEnabled(False)
            self.ui.btn_nav_accounts.setEnabled(False)
            self.ui.btn_nav_loans.setEnabled(False)   

    def open_main(self):
        from controller.main_window_controller import MainWindowController
        self.main = MainWindowController()
        self.main.show()
        self.close()   # đóng form login
