import pymysql as MySQLdb

try:
    db = MySQLdb.connect(host='localhost', user='root', password='', db='thuvien')
    cur = db.cursor()
    
    cur.execute("SELECT * FROM books")
    data = cur.fetchall()
    
    print(f"Số lượng sách trong database: {len(data)}")
    for book in data:
        print(f"ID: {book[0]}, Title: {book[1]}, Code: {book[2]}, Quantity: {book[3]}")
        
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    if 'db' in locals():
        db.close()
