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
        
        # Xóa các thẻ cũ
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
        # Bố cục 4 cột
        cols = 4
        for idx, row in enumerate(rows):
            card = self.create_book_card(row)
            r = idx // cols
            c = idx % cols
            layout.addWidget(card, r, c)
            
        # Thêm một stretch vào hàng dưới cùng để đẩy tất cả các mục lên
        # Điều này ngăn các thẻ kéo dài theo chiều dọc nếu chỉ có một vài thẻ
        layout.setRowStretch(layout.rowCount(), 1)
    
    # Tạo thẻ sách
    def create_book_card(self, data):
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QPixmap
        from pathlib import Path
        
        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(210, 360)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Ảnh bìa
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
        title_label.setFixedHeight(45) # Ép chiều cao cố định
        title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Tác giả
        author_name = data.get("author_name") or "Không rõ"
        author_label = QLabel(author_name.upper())
        author_label.setStyleSheet("border: none; color: #8f95a3; font-size: 11px; font-weight: bold;")
        
        # Nút mượn sách
        btn = QPushButton("MƯỢN SÁCH")
        btn.setCursor(Qt.PointingHandCursor)
        if data.get("quantity", 0) > 0:
            btn.setObjectName("btn_borrow")
            btn.clicked.connect(lambda _, bid=data['id']: self._on_borrow_specific(bid))
        else:
            btn.setText("HẾT SÁCH")
            btn.setObjectName("btn_disabled")
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

