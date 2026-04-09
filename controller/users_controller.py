import pymysql
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt

from controller.combo_utils import fill_combobox_with_ids, set_combo_current_data
from model import author_model, book_model, category_model, publisher_model, account_model, user_model
from view.login_ui import Ui_mainWindow
from model.user_model import User
import hashlib

def _parse_int(text, default=0):
    text = (text or "").strip()
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


class UsersController:
    TAB_LIST = 0
    TAB_ADD = 1
    TAB_EDIT = 2

    def __init__(self, main_window: QMainWindow, screen):
        self._main = main_window
        self._screen = screen
    pass