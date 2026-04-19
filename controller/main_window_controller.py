from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget
from model.db import get_connection
from model.account_model import Account
import anhthuvien_rc
import re

from controller.authors_controller import AuthorsController
from controller.books_controller import BooksController
from controller.categories_controller import CategoriesController
from controller.publishers_controller import PublishersController
from controller.stats_controller import StatsController
from controller.accounts_controller import AccountsController
from controller.loans_controller import LoansController

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
        self.btn_logout.clicked.connect(self.handle_logout)

        self.setup_permissions()

    def setup_permissions(self):
        role = self._current_user.get('role') if self._current_user else None
        
        if role == 'reader':
            # Reader chỉ thấy Thống kê và Mượn/trả
            self.btn_nav_books.hide()
            self.btn_nav_categories.hide()
            self.btn_nav_authors.hide()
            self.btn_nav_publishers.hide()
            self.btn_nav_accounts.hide()
            # Chuyển về màn hình thống kê làm mặc định
            self._go(0)
        elif role == 'admin':
            # Admin thấy tất cả
            pass

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
            self._loans_ctrl.refresh_return_table()

    def handle_logout(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Đăng xuất")
        msg.setText("Bạn có chắc chắn muốn đăng xuất?")
        
        btn_yes = msg.addButton("Đăng xuất", QMessageBox.YesRole)
        btn_no = msg.addButton("Hủy", QMessageBox.NoRole)
        
        msg.exec_()
        
        if msg.clickedButton() == btn_yes:
            self.login_window = LoginWindow()
            self.login_window.showMaximized()
            self.close()
            
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(_VIEW_DIR / "login.ui"), self)
        self.ui = self

        # bắt sự kiện nút login
        self.ui.btn_login.clicked.connect(self.handle_login)
        # bắt sự kiện nút đăng ký
        self.ui.btn_regist_1.clicked.connect(self.open_regist)

    def handle_login(self):
        username = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()
        con = None
        try:
            con = get_connection()
            acc_model = Account(con)
            user = acc_model.check_admin_login(username, password) or acc_model.check_reader_login(username, password)
            if user:
                if 'role' in user and user['role']:
                    user['role'] = user['role'].lower()
                    if user['role'] == 'người dùng':
                        user['role'] = 'reader'         
                
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
                

    def open_main(self):
        from controller.main_window_controller import MainWindowController
        self.main = MainWindowController()
        self.main.showMaximized()
        self.close()   # đóng form login
        
    def open_regist(self):
        self.regist_window = RegistWindow()
        self.regist_window.showMaximized()
        self.close()   # đóng form login

class RegistWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(_VIEW_DIR / "regist.ui"), self)
        self.ui = self

        # bắt sự kiện nút đăng ký
        self.ui.btn_regist.clicked.connect(self.handle_regist)
        self.ui.btn_return_login.clicked.connect(self.open_login)

    def handle_regist(self):
        name = self.ui.lineEdit_name.text().strip()
        email = self.ui.lineEdit_email.text().strip()
        username = self.ui.lineEdit_username_2.text().strip()
        password = self.ui.lineEdit_password_regist.text().strip()

        if not all([name, email, username, password]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        # Kiểm tra định dạng Họ và tên
        name_pattern = r"^[a-zA-ZÀ-ỹ\s]{2,50}$"
        if not re.match(name_pattern, name):
            QMessageBox.warning(self, "Lỗi", "Họ và tên không hợp lệ!")
            return

        # Kiểm tra định dạng email (phải là @gmail.com)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ!")
            return

        # Kiểm tra định dạng Tên đăng nhập
        username_pattern = r"^[a-zA-Z0-9_]{3,20}$"
        if not re.match(username_pattern, username):
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập không hợp lệ (3-20 ký tự, alphanumeric)!")
            return

        # Kiểm tra định dạng Mật khẩu
        password_pattern = r'^[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_pattern, password):
            QMessageBox.warning(self, "Lỗi", f"Mật khẩu không hợp lệ (ít nhất 8 ký tự)!")
            return

        con = None
        try:
            con = get_connection()
            import model.account_model as account_model
            
            # Kiểm tra trùng email
            if account_model.find_by_email(email):
                QMessageBox.warning(self, "Lỗi", "Email đã tồn tại! Vui lòng sử dụng email khác.")
                return

            # Kiểm tra trùng username
            if account_model.find_by_username(username):
                QMessageBox.warning(self, "Lỗi", "Tên đăng nhập đã tồn tại! Vui lòng sử dụng tên khác.")
                return

            import hashlib
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            account_model.create_account(name, email, 'reader', username, hashed_password)

            QMessageBox.information(self, "Thành công", "Đăng ký tài khoản thành công!")
            self.open_login()
        finally:
            if con:
                con.close()

    def open_login(self):
        from controller.main_window_controller import LoginWindow
        self.login = LoginWindow()
        self.login.showMaximized()
        self.close()
