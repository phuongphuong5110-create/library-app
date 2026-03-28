import pymysql as MySQLdb

try:
    # Kết nối mà không cần database
    db = MySQLdb.connect(host='localhost', user='root', password='')
    cur = db.cursor()
    
    # Tạo database
    cur.execute("CREATE DATABASE IF NOT EXISTS thuvien")
    cur.execute("USE thuvien")
    
    # Tạo bảng category
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(100)
        )
    """)
    
    # Tạo bảng author
    cur.execute("""
        CREATE TABLE IF NOT EXISTS author (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100)
        )
    """)
    
    # Tạo bảng publisher
    cur.execute("""
        CREATE TABLE IF NOT EXISTS publisher (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100)
        )
    """)
    
    # Tạo bảng books
    cur.execute("DROP TABLE IF EXISTS books")
    cur.execute("""
        CREATE TABLE books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200),
            code VARCHAR(50),
            quantity INT,
            year INT,
            description TEXT,
            category VARCHAR(100),
            author VARCHAR(100),
            publisher VARCHAR(100)
        )
    """)
    
    # Thêm dữ liệu mẫu
    cur.execute("SELECT COUNT(*) FROM category")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO category (category_name) VALUES ('Văn học'), ('Khoa học'), ('Lịch sử')")
        
    cur.execute("SELECT COUNT(*) FROM author") 
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO author (name) VALUES ('Nguyễn Nhật Ánh'), ('Tô Hoài'), ('Vũ Trọng Phụng')")
        
    cur.execute("SELECT COUNT(*) FROM publisher")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO publisher (name) VALUES ('Nhà xuất bản Trẻ'), ('Nhà xuất bản Giáo dục'), ('Nhà xuất bản Văn học')")
    
    db.commit()
    print("Database và bảng đã được tạo thành công!")
    
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    if 'db' in locals():
        db.close()
