APP_STYLESHEET = """
QMainWindow {
    background-color: #f0f2f5;
}
QWidget#nav_panel {
    background-color: #1a2332;
    min-width: 200px;
    max-width: 240px;
}
QWidget#nav_panel QPushButton {
    background-color: #243044;
    color: #e8eaed;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
}
QWidget#nav_panel QPushButton:hover {
    background-color: #2d3d52;
}
QWidget#nav_panel QPushButton:pressed {
    background-color: #3d5280;
}
QWidget#nav_panel QPushButton#btn_logout {
    background-color: transparent;
    color: #f28b82;
    border: 1px solid #f28b82;
    margin-top: 20px;
}
QWidget#nav_panel QPushButton#btn_logout:hover {
    background-color: rgba(242, 139, 130, 0.2);
}
QFrame#card {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e6ea;
}
QLabel#card_value {
    font-size: 28px;
    font-weight: bold;
    color: #1a2332;
}
QLabel#card_label {
    font-size: 12px;
    color: #5f6368;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #dadce0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLineEdit, QPlainTextEdit {
    border: 1px solid #dadce0;
    border-radius: 6px;
    padding: 6px 10px;
    background-color: #ffffff;
    min-height: 22px;
}
QTableWidget {
    border: 1px solid #dadce0;
    border-radius: 8px;
    background-color: #ffffff;
    gridline-color: #e8eaed;
    selection-background-color: #e8f0fe;
    selection-color: #1a2332;
}
QHeaderView::section {
    background-color: #f1f3f4;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #dadce0;
    font-weight: bold;
}
QPushButton {
    background-color: #29b87e;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #1967d2;
}
QPushButton#btn_secondary {
    background-color: #ffffff;
    color: #29b87e;
    border: 1px solid #dadce0;
}
QPushButton#btn_secondary:hover {
    background-color: #f8f9fa;
}
QPushButton#btn_danger {
    background-color: #d93025;
}
QPushButton#btn_danger:hover {
    background-color: #b31412;
}
QPushButton#btn_books_delete, QPushButton#btn_edit_delete,
QPushButton#btn_category_delete, QPushButton#btn_author_delete,
QPushButton#btn_publisher_delete {
    background-color: #d93025;
}
QPushButton#btn_books_delete:hover, QPushButton#btn_edit_delete:hover,
QPushButton#btn_category_delete:hover, QPushButton#btn_author_delete:hover,
QPushButton#btn_publisher_delete:hover {
    background-color: #b31412;
}
QPushButton#btn_return_book {
    background-color: #ff0000;
    color: #ffffff;
}
QTabWidget::pane {
    border: 1px solid #dadce0;
    border-radius: 8px;
    background-color: #ffffff;
    top: -1px;
}
QTabBar::tab {
    padding: 10px 20px;
    margin-right: 4px;
    background-color: #f1f3f4;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    border-bottom: 2px solid #29b87e;
}
QComboBox QAbstractItemView {
    border: none;
    padding: 0px;
    margin: 0px;
    outline: 0;
}

QComboBox QAbstractItemView::item {
    height: 24px;
    padding: 0px 8px;
    margin: 0px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #e8f0fe;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #d2e3fc;
}
QLabel#status_overdue {
    color: #d93025;
    font-weight: bold;
}
QLabel#status_borrowed {
    color: #1a73e8;
    font-weight: bold;
}
QLabel#status_returned {
    color: #1e8e3e;
    font-weight: bold;
}
QLabel#status_pending {
    color: #f9ab00;
    font-weight: bold;
}
QPushButton#btn_disabled {
    background-color: #f4f6fb;
    color: #8f95a3;
    border-radius: 8px;
    padding: 8px 0;
    font-weight: bold;
    font-size: 12px;
    border: none;
}
QPushButton#btn_borrow {
    background-color: #29b87e;
    color: white;
    border-radius: 8px;
    padding: 8px 0;
    font-weight: bold;
    font-size: 12px;
    border: none;
}
QPushButton#btn_borrow:hover {
    background-color: #239e6c;
}
QFrame#card {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #e5eaf5;
}
QFrame#card:hover {
    border: 1px solid #29b87e;
}
"""
