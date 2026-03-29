# Tài liệu Giải thích Dự án Ứng dụng Quản lý Thư viện

Tài liệu này cung cấp một cái nhìn tổng quan và chi tiết về cấu trúc, luồng hoạt động và các thành phần của dự án "Ứng dụng Quản lý Thư viện" (`appthuvien`).

## 1. Tổng quan dự án

- **Ngôn ngữ lập trình**: Python
- **Giao diện người dùng (GUI)**: PyQt5 (có sử dụng PyQt Designer - fille `.ui`)
- **Cơ sở dữ liệu**: MySQL (được thao tác qua thư viện `pymysql`)
- **Kiến trúc**: Mô hình MVC (Model-View-Controller) tuy không quá chặt chẽ nhưng chia tách rõ ràng giữa Database (Model), Giao diện (View) và Xử lý logic (Controller).

## 2. Cấu trúc Thư mục

Dự án được sắp xếp theo các thư mục chính:

- `model/`: Chứa các file tương tác trực tiếp với cơ sở dữ liệu (`author_model.py`, `book_model.py`, `db.py`, ...).
- `view/`: Chứa các file giao diện người dùng `.ui` (tạo bởi Qt Designer).
- `controller/`: Chứa các file xử lý logic, liên kết giao diện (view) với dữ liệu (model).
- `sql/`: Chứa file `schema.sql` dùng để khởi tạo cơ sở dữ liệu.
- Các file ở thư mục gốc:
  - `main.py`: Điểm đầu vào (entry point) để chạy ứng dụng.
  - `app_config.py`: Quản lý việc đọc file cấu hình (`config.ini`).
  - `app_theme.py`: Chứa stylesheet (CSS/QSS) để làm đẹp giao diện PyQt5.
  - `setup_database.py`: Chạy lệnh khởi tạo database ban đầu.
  - `config.ini`: File chứa thông tin kết nối DB (user, password, host...).

## 3. Các thành phần Chi tiết

### 3.1. File cấu hình và Khởi động (`main.py`, `app_config.py`)
- **`main.py`**: Khởi tạo ứng dụng PyQt5 (`QApplication`), nạp theme (`APP_STYLESHEET`), khởi tạo cửa sổ chính `MainWindowController` và hiển thị nó.
- **`app_config.py`**: Đọc file `config.ini` (sao chép từ `config.example.ini`) để lấy các thông số kết nối Database (Host, Port, User, Password, Database Name).

### 3.2. Lớp Dữ liệu - Model (`model/`)
Model đảm nhiệm việc kết nối MySQL và thực thi các câu truy vấn SQL:
- **`db.py`**: Chứa hàm `get_connection()` dựa trên cấu hình lấy từ `app_config.py`. Đồng thời cung cấp context manager `cursor()` giúp tự động đóng/mở kết nối và commit rollback an toàn.
- **Các model nghiệp vụ** (`author_model.py`, `book_model.py`, `category_model.py`, `publisher_model.py`): Mỗi file chứa các hàm CRUD (Create, Read, Update, Delete) cho một bảng tương ứng.
  - Ví dụ `book_model.py`: Có hàm `insert_book`, `update_book`, `delete_by_id`, `list_for_stats_table`. Truy vấn trong book lấy thêm thông tin join từ bảng category, author, publisher để lấy tên hiển thị.

### 3.3. Lớp Giao diện - View (`view/`)
- Mọi file trong thư mục này đều có định dạng `.ui` (XML), được thiết kế bằng PyQt Designer.
- **`main_window.ui`**: Giao diện khung chứa ứng dụng, có thanh điều hướng (buttons) và một `QStackedWidget` để chuyển đổi giữa các màn hình (stats, books, authors...).
- **Các file screen_*.ui**: Là thiết kế riêng rẽ của từng màn hình thống kê, quản lý sách, tác giả, v.v.

### 3.4. Lớp Logic - Controller (`controller/`)
Controller đóng vai trò cầu nối, lắng nghe thao tác của người dùng trên View và gọi các hàm của Model để xử lý:
- **`main_window_controller.py`**: Kế thừa `QMainWindow`, nó nạp file `main_window.ui`. Nó khởi tạo các widget màn hình (từ `screen_*.ui`) và đưa vào `stacked_screens` (QStackedWidget). Nó cũng chứa logic click menu để chuyển tab (`_go(index)`).
- **Các file screen controller** (`books_controller.py`, `authors_controller.py`, `stats_controller.py`,...): Mỗi class controller nhận vào MainWindow và khung widget UI tương ứng.
  - Trong hàm khởi tạo (`__init__`), chúng ánh xạ (bind) các sự kiện click nút bấm (clicked.connect) tới các hàm xử lý.
  - Các controller gọi `model.*_model.py` để lấy dữ liệu đổ vào `QTableWidget` (hiển thị bảng) hoặc thêm/sửa/xoá dựa trên dữ liệu người dùng nhập trong các `QLineEdit`.
- **`combo_utils.py`**: File phụ trợ chứa các hàm để lấp đầy (fill) dữ liệu vào các Combobox (QComboBox).

### 3.5. Cơ sở dữ liệu - Database (`sql/schema.sql`)
Kịch bản khởi tạo database có cấu trúc 4 bảng chính:
- `categories`: Thể loại sách.
- `authors`: Tác giả sách.
- `publishers`: Nhà xuất bản.
- `books`: Chứa thông tin sách (title, code, quantity, year), liên kết khoá ngoại (Foreign Key) tới 3 bảng trên (category_id, author_id, publisher_id).

## 4. Luồng hoạt động (Workflow)
1. **Chạy ứng dụng**: Lệnh `python main.py` được thực thi.
2. **Setup**: `main.py` nạp cấu hình và tạo cửa sổ `MainWindowController`.
3. **Nạp giao diện**: `MainWindowController` đọc `view/main_window.ui`, sau đó nạp các screen rời rạc vào một StackedWidget để tiện chuyển trang.
4. **Hiển thị dữ liệu**: Khi chuyển sang trang "Quản lý Sách", `BooksController` gọi `book_model.list_for_stats_table()`. Model mở kết nối qua `db.py`, chạy SQL, trả về danh sách dict. Controller lấy mảng kết quả đó vẽ lên `QTableWidget`.
5. **Thao tác**: Người dùng nhấn "Thêm sách" -> Controller đọc text từ giao diện -> gọi `book_model.insert_book()` -> cập nhật lại Table UI. Kèm theo hiển thị thông báo ở StatusBar (nằm dưới cùng của MainWindow).

## 5. Kết luận
Kiến trúc dự án này khá rõ ràng, theo sát tư tưởng tách biệt UI và Code (`.ui` file + `.py` file) của PyQt5 kết hợp với một layer thao tác SQL thuần (PyMySQL) được đặt ở trong model. Dự án rất thích hợp cho việc quản lý desktop quy mô nhỏ với code minh bạch, dễ dàng mở rộng chức năng.
