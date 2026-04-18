CREATE DATABASE IF NOT EXISTS thuvien CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE thuvien;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS publishers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    code VARCHAR(50) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    year INT NOT NULL DEFAULT 0,
    description TEXT,
    category_id INT NOT NULL,
    author_id INT NOT NULL,
    publisher_id INT NOT NULL,
    CONSTRAINT fk_books_category FOREIGN KEY (category_id) REFERENCES categories(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_books_author FOREIGN KEY (author_id) REFERENCES authors(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_books_publisher FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    UNIQUE KEY uq_books_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    fullname VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'reader'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS loans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    books_id INT NOT NULL,
    code_id INT,
    authors_id INT,
    account_id INT,
    borrow_date DATE NOT NULL DEFAULT CURDATE(),
    due_date DATE,
    return_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'borrowed',
    note TEXT,
    CONSTRAINT fk_loans_book FOREIGN KEY (books_id) REFERENCES books(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_loans_account FOREIGN KEY (account_id) REFERENCES accounts(id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO categories (id, category_name) VALUES
 (1, 'Văn học'),
 (2, 'Khoa học'),
 (3, 'Lịch sử');

INSERT IGNORE INTO authors (id, name) VALUES
 (1, 'Nguyễn Nhật Ánh'),
 (2, 'Tô Hoài'),
 (3, 'Vũ Trọng Phụng');

INSERT IGNORE INTO publishers (id, name) VALUES
 (1, 'Nhà xuất bản Trẻ'),
 (2, 'Nhà xuất bản Giáo dục'),
 (3, 'Nhà xuất bản Văn học');

INSERT IGNORE INTO books (id, title, code, quantity, year, category_id, author_id, publisher_id) VALUES
 (1, 'Cô Gái Đến Từ Hôm Qua', 'CGDTFHQ001', 5, 2012, 1, 1, 1),
 (2, 'Tắt Đèn', 'TDDEN001', 3, 1939, 1, 3, 3),
 (3, 'Tìm Kiếm Trái Đất', 'TKTD001', 4, 1957, 3, 2, 2);

INSERT IGNORE INTO users (id, username, password, email, fullname, role) VALUES
 (1, 'admin', '123456', 'admin@library.com', 'Admin User', 'admin'),
 (2, 'user1', 'password', 'user1@email.com', 'Nguyễn Văn A', 'user');

INSERT IGNORE INTO accounts (id, name, email, role) VALUES
 (1, 'Admin User', 'admin@library.com', 'Admin'),
 (2, 'Nguyễn Văn A', 'nguyenvana@email.com', 'Người dùng'),
 (3, 'Trần Thị B', 'tranthib@email.com', 'Người dùng');
