import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt5.QtWidgets import QApplication

from app_theme import APP_STYLESHEET
from controller.main_window_controller import LoginWindow
#from controller.main_window_controller import MainWindowController

# Biến global để lưu thông tin user hiện tại
current_user = None

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = LoginWindow()
    # window = MainWindowController()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
