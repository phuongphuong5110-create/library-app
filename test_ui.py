import sys
from PyQt5.QtWidgets import QApplication
from controller.main_window_controller import MainWindowController

app = QApplication(sys.argv)
class MockUser:
    pass
import main
main.current_user = {'name': 'Phuong', 'role': 'reader'}

try:
    window = MainWindowController()
    print("Has btn_toggle_profile:", hasattr(window, 'btn_toggle_profile'))
    print("Text:", window.btn_toggle_profile.text() if hasattr(window, 'btn_toggle_profile') else "N/A")
except Exception as e:
    import traceback
    traceback.print_exc()

