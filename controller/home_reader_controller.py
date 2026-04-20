from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

from model import book_model


class HomeReaderController:
    def __init__(self, main_window: QMainWindow, screen, loans_controller=None):
        self._main = main_window
        self._screen = screen
        self._loans_ctrl = loans_controller

        if hasattr(self._screen, "btn_home_refresh"):
            self._screen.btn_home_refresh.clicked.connect(self.refresh)
        if hasattr(self._screen, "btn_home_search"):
            self._screen.btn_home_search.clicked.connect(self._on_search)
        if hasattr(self._screen, "edit_home_search"):
            self._screen.edit_home_search.returnPressed.connect(self._on_search)
        self.refresh()

    def refresh(self):
        search_text = ""
        if hasattr(self._screen, "edit_home_search"):
            search_text = self._screen.edit_home_search.text().strip()
        try:
            rows = book_model.list_available(search_text or None)
        except Exception:
            self._main.statusBar().showMessage(
                self._main.tr("Không thể tải danh sách sách.")
            )
            return

        layout = self._screen.grid_layout_books
        
        # Clear existing cards
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
        # Card Layout Setup
        # Use 4 columns layout
        cols = 4
        for idx, row in enumerate(rows):
            card = self.create_book_card(row)
            r = idx // cols
            c = idx % cols
            layout.addWidget(card, r, c)
            
        # Add a stretch to the bottom row to push all items up
        # This prevents cards from stretching vertically if there are only a few
        layout.setRowStretch(layout.rowCount(), 1)
        
    def create_book_card(self, data):
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QPixmap
        from pathlib import Path
        
        card = QFrame()
        card.setFixedSize(210, 360)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5eaf5;
            }
            QFrame:hover {
                border: 1px solid #29b87e;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Cover Image container (for styling)
        img_container = QWidget()
        img_container.setFixedSize(180, 220)
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(0, 0, 0, 0)
        
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        
        cover_path = data.get("cover_path")
        if cover_path:
            try:
                p = Path(cover_path)
                if p.is_file():
                    pix = QPixmap(str(p))
                    img_label.setPixmap(pix.scaled(180, 220, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                else:
                    img_label.setText("No Image")
                    img_label.setStyleSheet("background-color: #f4f6fb; border-radius: 8px;")
            except Exception:
                img_label.setText("Lỗi")
        else:
            img_label.setText("No Image")
            img_label.setStyleSheet("background-color: #f4f6fb; border-radius: 8px;")
            
        img_layout.addWidget(img_label)
                
        # Title
        title_text = data.get("title") or "Không tên"
        # Cắt bớt nếu chữ quá dài để tránh vỡ khung thẻ
        if len(title_text) > 45:
            title_text = title_text[:42] + "..."
            
        title_label = QLabel(title_text)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("border: none; font-weight: bold; font-size: 14px; color: #1a1e29; margin-top: 5px;")
        title_label.setFixedHeight(45) # Ép chiều cao cố định để thẻ luôn cân đối bằng nhau
        title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Author
        author_name = data.get("author_name") or "Không rõ"
        author_label = QLabel(author_name.upper())
        author_label.setStyleSheet("border: none; color: #8f95a3; font-size: 11px; font-weight: bold;")
        
        # Button
        btn = QPushButton("MƯỢN SÁCH")
        btn.setCursor(Qt.PointingHandCursor)
        if data.get("quantity", 0) > 0:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #29b87e;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 0;
                    font-weight: bold;
                    font-size: 12px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #239e6c;
                }
            """)
            btn.clicked.connect(lambda _, bid=data['id']: self._on_borrow_specific(bid))
        else:
            btn.setText("HẾT SÁCH")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f4f6fb;
                    color: #8f95a3;
                    border-radius: 8px;
                    padding: 8px 0;
                    font-weight: bold;
                    font-size: 12px;
                    border: none;
                }
            """)
            btn.setEnabled(False)
            
        layout.addWidget(img_container)
        layout.addWidget(title_label)
        layout.addWidget(author_label)
        layout.addStretch()
        layout.addWidget(btn)
        
        return card

    def _on_search(self):
        self.refresh()

    def _on_borrow_specific(self, bid):
        if not self._loans_ctrl or not hasattr(self._loans_ctrl, "open_add_loan_dialog_with_book"):
            QMessageBox.warning(
                self._main,
                self._main.tr("Thông báo"),
                self._main.tr("Chức năng mượn sách chưa sẵn sàng."),
            )
            return
        self._loans_ctrl.open_add_loan_dialog_with_book(bid)

