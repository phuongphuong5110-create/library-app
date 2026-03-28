# Ứng dụng quản lý thư viện (PyQt5 + MySQL)

Cấu trúc **MVC**: thư mục `model` (truy cập dữ liệu), `view` (file `.ui`), `controller` (logic và kết nối giao diện với model).

## Yêu cầu

- Python 3.8+
- MySQL Server (local hoặc remote)

## Cài đặt

```bash
cd appthuvien
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cấu hình cơ sở dữ liệu

1. Sao chép file mẫu:

   ```bash
   cp config.example.ini config.ini
   ```

2. Sửa `config.ini`: `host`, `port`, `user`, `password`, `database` cho đúng MySQL của bạn.

## Tạo database

Import schema (một lần, hoặc khi cần tạo lại cấu trúc bảng):

```bash
mysql -u root -p < sql/schema.sql
```

Hoặc dùng script Python (không xóa dữ liệu sách khi chạy lại):

```bash
python setup_database.py
```

Tên bảng trong schema: `categories`, `authors`, `publishers`, `books`. Nếu bạn đang dùng database cũ với tên bảng số ít (`category`, `author`, `publisher`), cần đổi tên bảng trong MySQL hoặc tạo database mới rồi import lại `sql/schema.sql`.

## Chạy chương trình

```bash
python main.py
```

Chạy bằng `main.py`: giao diện nằm trong `view/` (mỗi màn một file `.ui`), logic trong `controller/` và `model/`.

## Thông điệp giao diện

Chuỗi hiển thị động (status bar, lỗi) dùng `tr()` để có thể thêm file dịch `.qm` sau này.
