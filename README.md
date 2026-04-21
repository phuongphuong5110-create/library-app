# 📚 Ứng dụng Quản lý Thư viện (Library Management Application)

> Ứng dụng desktop quản lý thư viện toàn diện được xây dựng với **PyQt5** và **MySQL**, theo mô hình kiến trúc **MVC** (Model-View-Controller).

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu hình](#cấu-hình)
- [Sử dụng](#sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Kiến trúc ứng dụng](#kiến-trúc-ứng-dụng)
- [Các tính năng chính](#các-tính-năng-chính)
- [Hướng dẫn phát triển](#hướng-dẫn-phát-triển)

---

## 🎯 Tổng quan

**Ứng dụng Quản lý Thư viện** (AppThưViện) là một giải pháp toàn diện dành cho việc quản lý tài nguyên sách trong thư viện hoặc tổ chức. Ứng dụng hỗ trợ:

- 📖 Quản lý danh mục sách (thêm, sửa, xóa, tìm kiếm)
- ✍️ Quản lý tác giả, nhà xuất bản, thể loại
- 👥 Quản lý tài khoản độc giả
- 📤 Quản lý khoản vay/trả sách
- 📊 Thống kê và báo cáo
- 🔐 Xác thực người dùng (đăng nhập)

### Công nghệ sử dụng

| Thành phần | Công nghệ |
|-----------|-----------|
| **Giao diện** | PyQt5 + Qt Designer |
| **Cơ sở dữ liệu** | MySQL 5.7+ |
| **Ngôn ngữ** | Python 3.8+ |
| **Driver DB** | PyMySQL |
| **Bảo mật** | bcrypt (mã hóa mật khẩu) |

---

## 💻 Yêu cầu hệ thống

### Yêu cầu tối thiểu

- **Python**: 3.8 trở lên
- **MySQL Server**: 5.7 trở lên (local hoặc remote)
- **RAM**: 512MB
- **Disk**: 100MB
- **OS**: Windows, macOS, Linux

### Cài đặt MySQL

**macOS (Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian:**
```bash
sudo apt-get install mysql-server
sudo systemctl start mysql
```

**Windows:**
- Tải từ [MySQL Community Downloads](https://dev.mysql.com/downloads/mysql/)
- Chạy installer và hoàn tất cài đặt

---

## 🚀 Cài đặt

### 1. Clone/Tải dự án

```bash
cd /đường/dẫn/đến/dự/án
# hoặc git clone nếu dùng git
```

### 2. Tạo môi trường ảo (Virtual Environment)

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

**Danh sách dependencies:**
- `PyQt5>=5.15.0` - Framework giao diện
- `pymysql>=1.0.0` - Driver kết nối MySQL
- `bcrypt>=4.0.0` - Mã hóa mật khẩu

---

## ⚙️ Cấu hình

### 1. Khởi tạo file cấu hình

Nếu file `config.ini` chưa tồn tại:

```bash
cp config.example.ini config.ini
```

### 2. Sửa file `config.ini`

```ini
[database]
host = localhost          # Địa chỉ MySQL server
port = 3306              # Cổng MySQL (mặc định: 3306)
user = root              # Username MySQL
password = your_password # Password MySQL
database = appthuvien    # Tên database
```

**Lưu ý:** 
- Thay `your_password` bằng mật khẩu MySQL của bạn
- Nếu MySQL chạy trên máy khác, đổi `localhost` thành địa chỉ IP/hostname
- Tạo database nếu chưa tồn tại: `CREATE DATABASE appthuvien;`

### 3. Khởi tạo cơ sở dữ liệu

#### Cách 1: Dùng script Python (Khuyên dùng)

```bash
python setup_database.py
```

Script này sẽ:
- Đọc file `sql/schema.sql`
- Tạo các bảng (nếu chưa tồn tại)
- Không xóa dữ liệu hiện có

#### Cách 2: Import trực tiếp qua MySQL CLI

```bash
mysql -u root -p appthuvien < sql/schema.sql
```

Nhập mật khẩu MySQL khi được yêu cầu.

#### Cách 3: Dùng MySQL Workbench

1. Mở MySQL Workbench
2. Kết nối đến MySQL server
3. File → Open SQL Script → chọn `sql/schema.sql`
4. Click "Execute" (⚡)

---

## 🎮 Sử dụng

### Khởi chạy ứng dụng

```bash
python main.py
```

Ứng dụng sẽ:
- Đăng nhập (có sẵn tài khoản demo)
- Hiển thị màn hình chính
- Tìm tấy nhập liệu ở thanh điều hướng bên trái

### Màn hình chính

```
┌─────────────────────────────────────────┐
│  📚 Ứng dụng Quản lý Thư viện           │
├──────────┬──────────────────────────────┤
│ • Stats  │                              │
│ • Books  │  Nội dung màn hình chính     │
│ • Authors│                              │
│ • Publishers                             │
│ • Categories                             │
│ • Loans  │                              │
│ • Accounts                               │
│ • Logout │                              │
└──────────┴──────────────────────────────┘
```

### Hướng dẫn sử dụng từng module

#### 📖 Quản lý Sách

1. Chọn tab **Books** từ menu trái
2. Bảng sách sẽ hiển thị danh sách
3. **Thêm sách mới:**
   - Click nút "Add New" hoặc "Thêm"
   - Điền thông tin (Tên sách, Tác giả, NXB, Thể loại, Năm xuất bản, Số lượng)
   - Click "Save"
4. **Sửa thông tin:** Click vào dòng → sửa → "Update"
5. **Xóa sách:** Chọn sách → "Delete"

#### ✍️ Quản lý Tác giả / Nhà xuất bản / Thể loại

Tương tự như quản lý sách, có các nút:
- ➕ **Add**: Thêm mới
- ✏️ **Edit**: Sửa
- ❌ **Delete**: Xóa
- 🔍 **Search**: Tìm kiếm

#### 👥 Quản lý Tài khoản Độc giả

- Xem danh sách tài khoản
- Kích hoạt/vô hiệu hóa tài khoản
- Xem lịch sử khoản vay

#### 📤 Quản lý Khoản vay

- **Tạo khoản vay:** Chọn độc giả + sách → "Borrow"
- **Trả sách:** Chọn khoản vay → "Return"
- **Tính phí quá hạn:** Tự động tính dựa trên ngày hôm nay

#### 📊 Thống kê

Hiển thị:
- Tổng số sách
- Tổng độc giả
- Sách được mượn nhiều nhất
- Độc giả mượn nhiều nhất
- Thống kê theo thể loại

---

## 📁 Cấu trúc dự án

```
appthuvien/
├── main.py                          # Điểm vào (entry point)
├── app_config.py                    # Quản lý cấu hình
├── app_theme.py                     # Theme/Stylesheet (CSS)
├── config.ini                       # Cấu hình database (git-ignored)
├── config.example.ini               # Mẫu file cấu hình
├── requirements.txt                 # Dependencies
├── setup_database.py                # Script khởi tạo DB
├── PROJECT_EXPLANATION.md           # Tài liệu chi tiết dự án
│
├── model/                           # Lớp Model (Truy cập dữ liệu)
│   ├── db.py                        # Kết nối MySQL, context manager
│   ├── migrations.py                # Migration và versioning schema
│   ├── account_model.py             # CRUD Tài khoản
│   ├── book_model.py                # CRUD Sách
│   ├── author_model.py              # CRUD Tác giả
│   ├── category_model.py            # CRUD Thể loại
│   ├── publisher_model.py           # CRUD Nhà xuất bản
│   └── loans_model.py               # CRUD Khoản vay
│
├── view/                            # Lớp View (Giao diện)
│   ├── main_window.ui               # Giao diện chính (Designer)
│   ├── main_window.py               # Main window controller
│   ├── login.ui                     # Màn hình đăng nhập
│   ├── login_ui.py                  # Logic đăng nhập
│   ├── screen_books.ui              # Màn hình quản lý sách
│   ├── screen_authors.ui            # Màn hình quản lý tác giả
│   ├── screen_publishers.ui         # Màn hình quản lý NXB
│   ├── screen_categories.ui         # Màn hình quản lý thể loại
│   ├── screen_loans.ui              # Màn hình quản lý khoản vay
│   ├── screen_accounts.ui           # Màn hình quản lý tài khoản
│   ├── screen_stats.ui              # Màn hình thống kê
│   ├── dialog_loans.ui              # Dialog tạo khoản vay
│   ├── regist.ui                    # Màn hình đăng ký
│   └── anhthuvien.qrc               # Tài nguyên (ảnh, icon)
│
├── controller/                      # Lớp Controller (Logic)
│   ├── main_window_controller.py    # Controller chính, quản lý Login/Logout
│   ├── home_reader_controller.py    # Trang chủ độc giả
│   ├── books_controller.py          # Logic quản lý sách
│   ├── authors_controller.py        # Logic quản lý tác giả
│   ├── publishers_controller.py     # Logic quản lý NXB
│   ├── categories_controller.py     # Logic quản lý thể loại
│   ├── loans_controller.py          # Logic quản lý khoản vay
│   ├── accounts_controller.py       # Logic quản lý tài khoản
│   ├── stats_controller.py          # Logic thống kê
│   └── combo_utils.py               # Utility functions (điền combo box)
│
├── sql/                             # Scripts database
│   └── schema.sql                   # Schema, bảng, relationships
│
├── assets/                          # Tài nguyên (ảnh, file)
│   └── book_covers/                 # Ảnh bìa sách
│
└── .venv/                           # Virtual environment (không commit)
```

---

## 🏗️ Kiến trúc ứng dụng

### Mô hình MVC (Model-View-Controller)

```
┌─────────────────────────────────────────────┐
│           Người dùng (User)                 │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────┐
    │   View (Giao diện)      │
    │ - main_window.ui        │
    │ - screen_*.ui           │
    │ - dialog_*.ui           │
    └────────────┬────────────┘
                  │ (User tương tác)
                  ▼
    ┌─────────────────────────┐
    │  Controller (Logic)     │
    │ - *_controller.py       │
    │ - Xử lý sự kiện        │
    │ - Validate dữ liệu     │
    └────────────┬────────────┘
                  │ (Gọi hàm)
                  ▼
    ┌─────────────────────────┐
    │  Model (Dữ liệu)        │
    │ - *_model.py            │
    │ - CRUD operations       │
    └────────────┬────────────┘
                  │ (Execute SQL)
                  ▼
    ┌─────────────────────────┐
    │  Database (MySQL)       │
    └─────────────────────────┘
```

### Luồng hoạt động (Workflow)

```
1. Khởi động (main.py)
   ↓
2. Đọc cấu hình (app_config.py)
   ↓
3. Kiểm tra/Cấp nhật schema DB (migrations.py)
   ↓
4. Hiển thị màn hình đăng nhập (LoginWindow)
   ↓
5. Xác thực tài khoản (kiểm tra mật khẩu bcrypt)
   ↓
6. Nếu thành công → MainWindowController
   ↓
7. Hiển thị menu + content area (QStackedWidget)
   ↓
8. User click menu → MainWindowController chuyển tab
   ↓
9. Tab mới hiển thị data từ Model → DB
   ↓
10. User nhập dữ liệu + click Save/Update/Delete
    ↓
11. Controller gọi Model → Model gọi DB.py
    ↓
12. Execute SQL query → Cập nhật UI
```

### Class Diagram (Tóm tắt)

```
[QApplication]
    └── [LoginWindow]  (login_ui.py + LoginWindow)
            └── [MainWindowController] (main_window_controller.py)
                ├── [BooksController]    (books_controller.py)
                ├── [AuthorsController]  (authors_controller.py)
                ├── [PublishersController] (publishers_controller.py)
                ├── [CategoriesController] (categories_controller.py)
                ├── [LoansController]    (loans_controller.py)
                ├── [AccountsController] (accounts_controller.py)
                └── [StatsController]    (stats_controller.py)

[Database]
    ├── [accounts]    (username, password, role, active)
    ├── [books]       (title, code, quantity, year, cover_path)
    ├── [authors]     (name, bio)
    ├── [publishers]  (name, address)
    ├── [categories]  (name, description)
    └── [loans]       (book_id, account_id, borrow_date, due_date, return_date)

[Models]
    ├── [db.py]                    (get_connection, cursor)
    ├── [account_model.py]         (authenticate, create, list...)
    ├── [book_model.py]            (CRUD books)
    ├── [author_model.py]          (CRUD authors)
    ├── [publisher_model.py]       (CRUD publishers)
    ├── [category_model.py]        (CRUD categories)
    └── [loans_model.py]           (CRUD loans)
```

---

## ✨ Các tính năng chính

### 🔐 Xác thực & Bảo mật
- ✅ Đăng nhập với username/password
- ✅ Mã hóa mật khẩu (bcrypt)
- ✅ Phân quyền (Admin/User)
- ✅ Session management
- ✅ Đăng xuất an toàn

### 📚 Quản lý Tài nguyên
- ✅ **Sách**: Thêm/sửa/xóa, tìm kiếm, lọc theo thể loại
- ✅ **Tác giả**: Quản lý tác giả, liên kết với sách
- ✅ **Nhà xuất bản**: Quản lý NXB, liên kết với sách
- ✅ **Thể loại**: Quản lý danh mục, phân loại sách
- ✅ **Ảnh bìa**: Lưu trữ và hiển thị ảnh bìa sách

### 👥 Quản lý Độc giả
- ✅ Tạo tài khoản độc giả
- ✅ Xem thông tin chi tiết
- ✅ Kích hoạt/vô hiệu hóa tài khoản
- ✅ Xem lịch sử mượn sách

### 📤 Quản lý Khoản Vay
- ✅ Tạo khoản vay mới (borrow)
- ✅ Trả sách (return)
- ✅ Tính phí quá hạn tự động
- ✅ Lịch sử giao dịch
- ✅ Cảnh báo sách quá hạn

### 📊 Thống kê & Báo cáo
- ✅ Tổng số sách/độc giả
- ✅ Sách được mượn nhiều nhất
- ✅ Độc giả mượn nhiều nhất
- ✅ Thống kê theo thể loại
- ✅ Tỷ lệ sách có sẵn

### 🎨 Giao diện
- ✅ Theme tối/sáng (QSS stylesheet)
- ✅ Responsive layout
- ✅ Biểu tượng trực quan
- ✅ Thông báo user-friendly
- ✅ Tables với sorting/filtering

---

## 🛠️ Hướng dẫn phát triển

### Môi trường phát triển

```bash
# Kích hoạt virtual environment
source .venv/bin/activate

# Cài thêm tools phát triển
pip install pylint black pytest pytest-cov flake8

# Kiểm tra style code
black controller/ model/ view/

# Lint
flake8 controller/ model/ view/
```

### Thêm tính năng mới

#### 1. Tạo Model (Database layer)

File: `model/feature_model.py`
```python
from model.db import cursor

def get_all_features():
    """Lấy tất cả features"""
    with cursor() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM features")
            return cur.fetchall()

def insert_feature(name, description):
    """Thêm feature mới"""
    with cursor() as conn:
        with conn.cursor() as cur:
            sql = "INSERT INTO features (name, description) VALUES (%s, %s)"
            cur.execute(sql, (name, description))
            conn.commit()
```

#### 2. Tạo View (UI layer)

- Mở [Qt Designer](https://doc.qt.io/qt-5/qtdesigner-manual.html)
- Tạo file `.ui` mới
- Thiết kế giao diện
- Lưu file `view/screen_feature.ui`
- PyQt sẽ tự động generate `.py` file

#### 3. Tạo Controller (Logic layer)

File: `controller/feature_controller.py`
```python
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.uic import loadUi
from model.feature_model import get_all_features, insert_feature

class FeatureController(QWidget):
    def __init__(self, main_window, screen_widget):
        super().__init__()
        self.main_window = main_window
        self.screen_widget = screen_widget
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Thiết lập UI - bind events"""
        self.screen_widget.add_btn.clicked.connect(self.add_feature)
    
    def load_data(self):
        """Tải dữ liệu từ DB"""
        features = get_all_features()
        # Cập nhật UI...
    
    def add_feature(self):
        """Thêm feature mới"""
        name = self.screen_widget.name_input.text()
        description = self.screen_widget.desc_input.text()
        
        if not name:
            QMessageBox.warning(self, "Error", "Name required!")
            return
        
        try:
            insert_feature(name, description)
            QMessageBox.information(self, "Success", "Feature added!")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
```

#### 4. Đăng ký Controller

File: `controller/main_window_controller.py` (thêm vào MainWindowController)
```python
from controller.feature_controller import FeatureController

# Trong __init__:
self.feature_screen = loadUi(os.path.join(UI_PATH, 'screen_feature.ui'))
self.stacked_screens.addWidget(self.feature_screen)
FeatureController(self, self.feature_screen)

# Thêm nút menu:
self.feature_btn = QPushButton("Features")
self.feature_btn.clicked.connect(lambda: self.go(index))  # index = số thứ tự
```

### Debug & Testing

```bash
# Chạy ứng dụng với debug
python -m pdb main.py

# Unit test
pytest tests/ -v

# Test coverage
pytest --cov=model --cov=controller tests/

# Xem logs
tail -f logs/app.log
```

### Database Migration

Khi cần thay đổi schema:

1. Sửa `sql/schema.sql`
2. Cập nhật version trong `model/migrations.py`
3. Thêm migration function
4. Chạy `python setup_database.py`

---

## 📝 Ghi chú

### Tên bảng Database

⚠️ **Lưu ý**: Schema hiện tại sử dụng tên số nhiều (plural):
- `categories` (không phải `category`)
- `authors` (không phải `author`)
- `publishers` (không phải `publisher`)
- `books`
- `accounts`
- `loans`

Nếu database cũ dùng số ít, cần rename hoặc tạo database mới.

### Hỗ trợ Docker (Tùy chọn)

```bash
# Nếu dùng Docker Compose
docker-compose up -d

# Chạy ứng dụng
python main.py
```

### Troubleshooting

| Lỗi | Giải pháp |
|-----|----------|
| `No module named 'PyQt5'` | Chạy `pip install PyQt5` |
| `Can't connect to MySQL server` | Kiểm tra config.ini, MySQL có chạy không |
| `Table doesn't exist` | Chạy `python setup_database.py` |
| `Permission denied` | Kiểm tra quyền file/folder hoặc sudo |
| `Port already in use` | Đổi port trong config.ini |

---

## 📚 Tài liệu tham khảo

- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)

---

## 📄 License

Project này được tạo cho mục đích học tập và đào tạo.

---

## 👨‍💻 Tác giả & Đóng góp

Được phát triển như một dự án thực hành Python GUI + Database.

---

## ❓ Hỗ trợ & Liên hệ

Nếu bạn gặp vấn đề:
1. Kiểm tra phần [Troubleshooting](#troubleshooting)
2. Xem lại file `PROJECT_EXPLANATION.md`
3. Kiểm tra logs của ứng dụng
4. Đảm bảo cấu hình database đúng

---

**Cảm ơn bạn đã sử dụng Ứng dụng Quản lý Thư viện! 📚**

Chạy bằng `main.py`: giao diện nằm trong `view/` (mỗi màn một file `.ui`), logic trong `controller/` và `model/`.

## Thông điệp giao diện

