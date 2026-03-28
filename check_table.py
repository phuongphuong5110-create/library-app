import pymysql as MySQLdb

try:
    db = MySQLdb.connect(host='localhost', user='root', password='', db='thuvien')
    cur = db.cursor()
    
    cur.execute("DESCRIBE books")
    columns = cur.fetchall()
    
    print("Cấu trúc bảng books :")
    for col in columns:
        print(col)
        
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    if 'db' in locals():
        db.close()
