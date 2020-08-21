import sys
from ui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView
from PyQt5 import QtSql
from PyQt5 import QtCore
import pandas as pd
import sqlite3

class form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('fieldlist.db')
        self.model = QtSql.QSqlTableModel()
        self.model.setTable('supply')
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.select()

        self.model.setHeaderData(1, QtCore.Qt.Horizontal,"نام کالا")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal,"صرفه جویی")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal,"مقدار/تعداد")
        self.ui.tableWidget.setModel(self.model)

        self.ui.pushButton.clicked.connect(self.addToDb)
        self.show()
        self.ui.pushButton_2.clicked.connect(self.updaterow)
        self.ui.pushButton_3.clicked.connect(self.delrow)
        self.ui.pushButton_4.clicked.connect(self.coming_back)
        self.i = self.model.rowCount()
        self.ui.lcdNumber.display(self.i)
        print(self.ui.tableWidget.currentIndex().row())

        self.readExcel()

    def coming_back(self):
        try:
            record = self.model.record(self.ui.tableWidget.currentIndex().row())
            sqliteCon = sqlite3.connect('fieldlist.db')
            cursor = sqliteCon.cursor()
            print('connected to sqlite')
            sql_read_query = "SELECT * from supply"
            cursor.execute(sql_read_query)
            result = cursor.fetchall()
            for row in result:
                kg = int(row[3]) + int(row[2])
                sql_query = """UPDATE supply SET kg = ? , sj = 0 WHERE id=?"""
                cursor.execute(sql_query,(kg,row[0]))
            sqliteCon.commit()
            print("Record Updated successfully ")
            cursor.close()
            record.setValue("sj",0)
            record.setValue("kg",kg)
            self.model.setRecord(self.ui.tableWidget.currentIndex().row(), record)
            
        except sqlite3.Error as error:
            print("Failed to update multiple records of sqlite table", error)
        finally:
            if (sqliteCon):
                sqliteCon.close()
                print("The SQLite connection is closed")

    def readExcel(self):
        df = pd.read_excel('data.xlsx')
        # print(df['Row'][0])
        for i in df.index:
            print(df['Description'][i])

    def addToDb(self):
        # todo: Validation
        print(self.i)
        self.model.insertRows(self.i,1)
        # supply et    
        self.model.setData(self.model.index(self.i,1),self.ui.lineEdit.text())
        
        try:
            # sj et
            # if self.ui.lineEdit.text() == '' :
            self.model.setData(self.model.index(self.i,2), self.ui.lineEdit_2.text())
            # else:
                # در صورت خالی بودن ماخذ را گرفته و محاسبه نماید. باید دکمه اضافه شود
                # self.model.setData(self.model.index(self.i,1),(1500 - 1300) * 2)
        except ValueError:
            QMessageBox.question(self,'اخطار', "مقدار صرفه جویی حتما باید به عدد وارد شود", QMessageBox.Ok)

        try:
            self.model.setData(self.model.index(self.i,3), int(self.ui.lineEdit_3.text()))
        except ValueError:
            QMessageBox.question(self,'اخطار', "مقدار/تعداد حتما باید به عدد وارد شود", QMessageBox.Ok)
            
        self.model.submitAll()
        self.i += 1
        self.ui.lcdNumber.display(self.i)

    def delrow(self):
        if self.ui.tableWidget.currentIndex().row() > -1:
            self.model.removeRow(self.ui.tableWidget.currentIndex().row())
            self.i -= 1
            self.model.select()
            self.ui.lcdNumber.display(self.i)
        else:
            QMessageBox.question(self,'پیام', "لطفا قبل از فشردن دکمه یکی از فیلد ها را انتخاب کنید", QMessageBox.Ok)
            self.show()

    def updaterow(self):
        if self.ui.tableWidget.currentIndex().row() > -1:
            record = self.model.record(self.ui.tableWidget.currentIndex().row())
            try:
                record.setValue("kg",int(self.ui.lineEdit_3.text()))
            except ValueError:
                QMessageBox.question(self,'اخطار', "مقدار/تعداد حتما باید به عدد وارد شود", QMessageBox.Ok)
            try:
                record.setValue("sj",self.ui.lineEdit_2.text())
            except ValueError:
                QMessageBox.question(self,'اخطار', "صرفه جویی حتما باید به عدد وارد شود", QMessageBox.Ok)

            record.setValue("name", self.ui.lineEdit.text())
            self.model.setRecord(self.ui.tableWidget.currentIndex().row(), record)
        else:
            QMessageBox.question(self,'پیام', "لطفا قبل از فشردن دکمه یکی از فیلد ها را انتخاب کنید", QMessageBox.Ok)
            self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frm = form()
    sys.exit(app.exec_())