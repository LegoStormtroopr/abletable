"""
Widget definitions for JSON schema elements.
"""
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
import tempfile
from .csv2sqlite import convert
import sqlite3
import csv

from PyQt5.QtCore import QThread


class CSVDB(QtSql.QSqlDatabase):
    def simple_query(self, query):
        query = self.exec_(query)
        query.next() # Only do it once
        record = query.record()

        return dict(
            (str(record.field(i).name()), record.value(i))
            for i in range(record.count())
        )


class CSVLoadThread(QThread):

    def __init__(self, csv, db_name):
        QThread.__init__(self)
        self.csv = csv
        self.db_name = db_name

    def __del__(self):
        self.wait()

    def run(self):
        # your logic here
        self.dialect = convert(self.csv, self.db_name, "base")

class CSVSaveThread(QThread):

    def __init__(self, csv, db, dialect):
        QThread.__init__(self)
        self.csv = csv
        self.db = db
        self.dialect = dialect

    def __del__(self):
        self.wait()

    def run(self):
        # your logic here
        with open(self.csv, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, dialect=self.dialect)
            query = self.db.exec_('SELECT * FROM "base"')

            first = True
            while query.next():
                record = query.record()
                if first:
                    first = False
                    spamwriter.writerow([
                        str(record.field(i).name())
                        for i in range(record.count())
                    ])

                spamwriter.writerow([
                    record.value(i)
                    for i in range(record.count())
                ])


class Model(QtSql.QSqlTableModel):
    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.setTable('base')
        # print(str(self.lastError().text()))
        self.select()


class Sheet(QtWidgets.QWidget):
    csv_name = None
    db = None
    csv_dialect = 'excel'

    def __init__(self, *args, **kwargs):
        self.csv = kwargs.pop('csv', None)
        self.tab_manager = kwargs.pop('parent', None)
        super(Sheet, self).__init__(*args, **kwargs)

        # self.set_tab_text("# {}".format(csv))
        # self.set_tab_tooltip("Loading file {}".format(csv))
        self.content_region = QtWidgets.QScrollArea(self)

        self.table = QtWidgets.QTableView()
        self.table.setSortingEnabled(True)
        # self.tableModel = Model(db=self.db)
        # self.table.setModel(self.tableModel)
        self.table.show()

        self.content_region.setWidget(self.table)
        self.content_region.setWidgetResizable(True)

        vbox = QtWidgets.QVBoxLayout()
        # vbox.addWidget(self.menu)
        vbox.addWidget(self.content_region)
        vbox.setContentsMargins(0,0,0,0)

        self.setLayout(vbox)

        if self.csv:
            self.open_csv(self.csv)

    def save_csv(self):
        self.get_thread = CSVSaveThread(self.csv, self.db, self.csv_dialect)
        self.get_thread.start()

        # self.get_thread.finished.connect(self.done)

    def open_csv(self, file, **kwargs):
        self.csv = file
        self.db_name = tempfile.TemporaryFile(suffix='.db3').name
        # self.db_conn = sqlite3.connect(self.db_name)
        # self.db_conn.text_factory = str


        self.set_tab_text("# {}".format(self.csv))
        self.set_tab_tooltip("Loading file {}".format(self.csv))

        # active_db = convert(file, db_name, "base")
        self.get_thread = CSVLoadThread(file, self.db_name)
        self.get_thread.start()

        self.get_thread.finished.connect(self.done)

    def done(self):
        self.csv_dialect = self.get_thread.dialect
        self.db = CSVDB('QSQLITE')
        # self.db.addDatabase('QSQLITE', self.db_name)
        self.db.setDatabaseName(self.db_name)
        if not self.db.open():
            QtWidgets.QMessageBox.critical(None, QtWidgets.qApp.tr("Cannot open database"),
                QtWidgets.qApp.tr("Unable to establish a database connection.\n"
                "This example needs SQLite support. Please read "
                "the Qt SQL driver documentation for information "
                "how to build it.\n\n" "Click Cancel to exit."),
             QtWidgets.QMessageBox.Cancel)

        # self.tableModel.delete()
        self.tableModel = Model(db=self.db)
        self.table.setModel(self.tableModel)

        self.set_tab_text("{}".format(self.csv))
        self.set_tab_tooltip("{}".format(self.csv))

        # self.get_sheet_statistics()

    def set_tab_tooltip(self, text):
        self.tab_manager.setTabToolTip(self.tab_index(), text)

    def set_tab_text(self, text):
        self.tab_manager.setTabText(self.tab_index(), text)

    def tab_index(self):
        return self.tab_manager.indexOf(self)


    def get_sheet_statistics(self):
        self.db_name
        
        # c = self.db_conn.cursor()

        # try:
        query = 'SELECT COUNT(1) as count FROM "base"'
        # val = c.execute(query).fetchone()
        val = self.db.simple_query(query)#.next().result().record().value(0)

        print(val)

    def add_column(self, name=None):
        extra = name or "column__sam"
        # c = self.db_conn.cursor()
        # c.execute('''ALTER TABLE "base" ADD COLUMN ''' + extra + ''' INTEGER''')
        self.db.exec_('''ALTER TABLE "base" ADD COLUMN ''' + extra + ''' INTEGER''')

        self.tableModel.setTable('base')
        self.tableModel.select()
        # self.db_conn.commit()
