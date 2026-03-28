from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys 
import pymysql as MySQLdb
import os

from PyQt5.uic import loadUiType

ui,_ = loadUiType(os.path.join(os.path.dirname(__file__), 'thuvien.ui'))

class MainApp(QMainWindow, ui):
    def __init__(self):
        super(MainApp, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)
        # Qt Designer may generate invalid enum paths (QtCore.Qt.QLineEdit.Password)
        # in this environment; set password modes explicitly in Python
        self.lineEdit_13.setEchoMode(QLineEdit.Password)
        self.lineEdit_14.setEchoMode(QLineEdit.Password)
        self.lineEdit_15.setEchoMode(QLineEdit.Password)
        self.lineEdit_18.setEchoMode(QLineEdit.Password)
        self.handel_button()
        
        self.Show_Category()
        self.Show_Author()
        self.Show_Publisher()
        
        self.Show_Category_Combobox()
        self.Show_Author_Combobox()
        self.Show_Publisher_Combobox()


    def handel_UI_changes(self):
        self.Tab.tabBar().setVisible(False)

    def handel_button(self):
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton_5.clicked.connect(self.open_them_sach)
        self.pushButton_3.clicked.connect(self.open_user)
        self.pushButton_2.clicked.connect(self.open_edit_book)
        self.pushButton_4.clicked.connect(self.open_setting)

        self.pushButton_6.clicked.connect(self.Add_New_Book)

        # UI contains pushButton_21/22/23 for add category/author/publisher
        self.pushButton_21.clicked.connect(self.Add_Category)
        self.pushButton_22.clicked.connect(self.Add_Author)
        self.pushButton_23.clicked.connect(self.Add_Publisher)


    def on_pushButton_clicked(self):
        # Chuyển sang tab đầu tiên; chỉnh index tùy nhu cầu của bạn.
        self.Tab.setCurrentIndex(0)

    def open_them_sach(self):
        self.Tab.setCurrentIndex(1)

    def open_books_tab(self):
        self.Tab.setCurrentIndex(1)

    def open_user(self):
        self.Tab.setCurrentIndex(2)

    def open_edit_book(self):
        self.Tab.setCurrentIndex(1)

    def open_setting(self):
        self.Tab.setCurrentIndex(3)

#themsach
    def Add_New_Book(self):
        self.db = MySQLdb.connect(host='localhost', user='root', password='', db='thuvien')
        self.cur = self.db.cursor()

        book_title = self.lineEdit_3.text()
        book_code = self.lineEdit_4.text()
        book_quantity = self.lineEdit_20.text()
        book_year = self.lineEdit_19.text()
        book_description = self.lineEdit_5.text()
        book_category = self.comboBox_3.currentText()
        book_author = self.comboBox_4.currentText()
        book_publisher = self.comboBox_5.currentText()
        
        # Chuyển đổi sang số nguyên
        try:
            book_quantity = int(book_quantity) if book_quantity else 0
            book_year = int(book_year) if book_year else 0
        except ValueError:
            book_quantity = 0
            book_year = 0
        
        self.cur.execute('''
            INSERT INTO books (title, code, quantity, year, description, category, author, publisher)
            VALUES (%s , %s , %s , %s , %s , %s , %s , %s)
        ''' ,(book_title , book_code , book_quantity , book_year , book_description , book_category , book_author , book_publisher))

        self.db.commit()
        self.statusBar().showMessage('New Book Added')

        self.lineEdit_3.setText('')
        self.lineEdit_4.setText('')
        self.lineEdit_20.setText('')
        self.lineEdit_19.setText('')
        self.comboBox_3.setCurrentIndex(0)
        self.comboBox_4.setCurrentIndex(0)
        self.comboBox_5.setCurrentIndex(0)
        self.Show_All_Books()        
    def Show_All_Books(self):
        try:
            self.db = MySQLdb.connect(host='localhost', user='root', password='', db='thuvien')
            self.cur = self.db.cursor()
            
            self.cur.execute("SELECT * FROM books")
            data = self.cur.fetchall()
            for row, book in enumerate(data):
                print(f"Book {row+1}: {book}")
                
            self.db.close()
            
        except Exception as e:
            print(f"Lỗi khi hiển thị sách: {e}")        

    def Search_Books(self):
    
        self.db = MySQLdb.connect(host='localhost' , user='root' , password ='' , db='thuvien')
        self.cur = self.db.cursor()

        book_title = self.lineEdit_8.text()

        sql = ''' SELECT * FROM books WHERE title = %s'''
        self.cur.execute(sql , [(book_title)])

        data = self.cur.fetchone()

        print(data)
        self.lineEdit_8.setText(data[1])
        self.lineEdit_6.setPlainText(data[2])
        self.lineEdit_7.setText(data[3])
        self.comboBox_8.setCurrentText(data[4])
        self.comboBox_6.setCurrentText(data[5])
        self.comboBox_7.setCurrentText(data[6])

    def Edit_Books(self):
        self.db = MySQLdb.connect(host='localhost' , user='root' , password ='' , db='thuvien')
        self.cur = self.db.cursor()

        book_title = self.lineEdit_8.text()
        book_description = self.lineEdit_6.toPlainText()
        book_code = self.lineEdit_7.text()
        book_category = self.comboBox_8.currentText()
        book_author = self.comboBox_6.currentText()
        book_publisher = self.comboBox_7.currentText()

        search_book_title = self.lineEdit_8.text()

        self.cur.execute('''
            UPDATE books SET title=%s ,description=%s ,code=%s ,category=%s ,author=%s ,publisher=%s WHERE title = %s
        ''', (book_title,book_description,book_code,book_category,book_author,book_publisher , search_book_title))

        self.db.commit()
        self.statusBar().showMessage('book updated')
        self.Show_All_Books()

#user
    def Add_New_User(self):
        pass

    def Login(self):
        pass

    def Edit_User(self):
        pass

#category
    def Add_Category(self):
        self.db = MySQLdb.connect(host='localhost', user='root', password='', db='thuvien')
        self.cur = self.db.cursor()

        category_name = self.lineEdit_37.text()

        self.cur.execute('''INSERT INTO category (category_name) VALUES (%s)''', (category_name,))

        self.db.commit()
        self.statusBar().showMessage('Thể Loại Đã Được Lưu')
        self.Show_Category()
        self.lineEdit_37.setText('')
    
    def Show_Category(self):
        self.db = MySQLdb.connect(host = 'localhost' , user = 'root' , password = '' , db = 'thuvien')
        self.cur = self.db.cursor()

        self.cur.execute(''' SELECT category_name FROM category''')
        data = self.cur.fetchall()

        if data :
            self.tableWidget_3.setRowCount(0)
            self.tableWidget_3.insertRow(0)
            for row , form in enumerate(data):
                for column , item in enumerate(form) :
                    self.tableWidget_3.setItem(row , column , QTableWidgetItem(str(item)))
                    column += 1

                row_position = self.tableWidget_3.rowCount()
                self.tableWidget_3.insertRow(row_position)
                
    def Show_Category_Combobox(self):
        self.db = MySQLdb.connect(host = 'localhost', user = 'root', password = '', db = 'thuvien')
        self.cur = self.db.cursor()

        self.cur.execute(''' SELECT category_name FROM category ''')
        data = self.cur.fetchall()

        self.comboBox_3.clear()
        for category in data :
            self.comboBox_3.addItem(category[0])
            self.comboBox_8.addItem(category[0])


    def Add_Author(self):
        self.db = MySQLdb.connect(host='localhost', user='root', password='', db='thuvien')
        self.cur = self.db.cursor()

        author_name = self.lineEdit_38.text()

        self.cur.execute('''INSERT INTO author (name) VALUES (%s)''', (author_name,))

        self.db.commit()
        self.statusBar().showMessage('Tác Giả Đã Được Lưu')
        self.Show_Author()
        self.lineEdit_38.setText('')

    def Show_Author(self):
        self.db = MySQLdb.connect(host = 'localhost' , user = 'root' , password = '' , db = 'thuvien')
        self.cur = self.db.cursor()

        self.cur.execute(''' SELECT name FROM author''')
        data = self.cur.fetchall()

        if data :
            self.tableWidget_4.setRowCount(0)
            self.tableWidget_4.insertRow(0)
            for row , form in enumerate(data):
                for column , item in enumerate(form) :
                    self.tableWidget_4.setItem(row , column , QTableWidgetItem(str(item)))
                    column += 1

                row_position = self.tableWidget_4.rowCount()
                self.tableWidget_4.insertRow(row_position)
                
    def Show_Author_Combobox(self):
        self.db = MySQLdb.connect(host = 'localhost', user = 'root', password = '', db = 'thuvien')
        self.cur = self.db.cursor()

        self.cur.execute(''' SELECT name FROM author ''')
        data = self.cur.fetchall()

        self.comboBox_4.clear()
        for author in data :
            self.comboBox_4.addItem(author[0])
            self.comboBox_6.addItem(author[0])

    def Add_Publisher(self):
        self.db = MySQLdb.connect(host='localhost', user='root', password='', db='thuvien')
        self.cur = self.db.cursor()

        publisher_name = self.lineEdit_39.text()

        self.cur.execute('''INSERT INTO publisher (name) VALUES (%s)''', (publisher_name,))

        self.db.commit()
        self.statusBar().showMessage('Nhà Xuất Bản Đã Được Lưu')
        self.Show_Publisher()
        self.lineEdit_39.setText('')


        
    def Show_Publisher(self):
        self.db = MySQLdb.connect(host = 'localhost' , user = 'root' , password = '' , db = 'thuvien')
        self.cur = self.db.cursor()

        self.cur.execute(''' SELECT name FROM publisher''')
        data = self.cur.fetchall()

        if data :
            self.tableWidget_5.setRowCount(0)
            self.tableWidget_5.insertRow(0)
            for row , form in enumerate(data):
                for column , item in enumerate(form) :
                    self.tableWidget_5.setItem(row , column , QTableWidgetItem(str(item)))
                    column += 1

                row_position = self.tableWidget_5.rowCount()
                self.tableWidget_5.insertRow(row_position)
                
    def Show_Publisher_Combobox(self):
        self.db = MySQLdb.connect(host = 'localhost', user = 'root', password = '', db = 'thuvien')
        self.cur = self.db.cursor()

        self.cur.execute(''' SELECT name FROM publisher ''')
        data = self.cur.fetchall()

        self.comboBox_5.clear()
        for author in data :
            self.comboBox_5.addItem(author[0])
            self.comboBox_7.addItem(author[0])
        
def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()  