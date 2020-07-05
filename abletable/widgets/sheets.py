"""
Widget definitions for JSON schema elements.
"""
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
import tempfile
from ..csv2sqlite import convert
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

    def multirow_query(self, query, max_rows=None):
        query = self.exec_(query)

        while query.next(): # Only do it once
            record = query.record()

            yield dict(
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

        self.content_region = QtWidgets.QScrollArea(self)

        self.table = QtWidgets.QTableView()
        self.horiz_headers = self.table.horizontalHeader()
        self.horiz_headers.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horiz_headers.customContextMenuRequested.connect(self.show_horiz_context_menu)

        self.vert_headers = self.table.verticalHeader()
        self.vert_headers.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.vert_headers.customContextMenuRequested.connect(self.show_vert_context_menu)
        # self.table.setSortingEnabled(True)
        # self.tableModel = Model(db=self.db)
        # self.table.setModel(self.tableModel)
        self.table.horizontalHeader().setSectionsMovable(True)       
        self.table.horizontalHeader().setDragEnabled(True)

        self.table.horizontalHeader().setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.table.show()

        self.content_region.setWidget(self.table)
        self.content_region.setWidgetResizable(True)

        # self.dock = QtWidgets.QTabWidget()

        vbox = QtWidgets.QHBoxLayout()
        vbox.addWidget(self.content_region)
        # vbox.addWidget(self.dock)
        vbox.setContentsMargins(0,0,0,0)

        self.setLayout(vbox)


        # hbox = QtWidgets.QHBoxLayout()

        # self.setLayout(hbox)

        if self.csv:
            self.open_csv(self.csv)

    def show_horiz_context_menu(self, position):
        column = self.horiz_headers.logicalIndexAt(position)
        menu = QtWidgets.QMenu()
        set_column_width = QtWidgets.QAction('Column width...', self,
            triggered = lambda *x: self.handle_resize_column(column, *x)
        )

        menu.addAction(set_column_width)
        menu.exec_(self.mapToGlobal(position))
        #menu.popup(QtGui.QCursor.pos())

    def show_vert_context_menu(self, position):
        column = self.vert_headers.logicalIndexAt(position)
        menu = QtWidgets.QMenu()
        set_row_height = QtWidgets.QAction('Row height...', self,
            triggered = lambda *x: self.handle_resize_row(column, *x)
        )

        menu.addAction(set_row_height)
        menu.exec_(self.mapToGlobal(position))

    def handle_resize_column(self, column, *args):
        width, ok = QtWidgets.QInputDialog.getInt(
            self, "Column Width", "Column width:",
            value = self.table.columnWidth(column), min = 0, max = 5000
        )
        if ok and width and int(width) > 2:
            self.table.setColumnWidth(column, width)

    def handle_resize_row(self, row, *args):
        height, ok = QtWidgets.QInputDialog.getInt(
            self, "Row Height", "Row height:",
            value = self.table.rowHeight(row), min = 0, max = 5000
        )
        if ok and height and int(height) > 2:
            self.table.setRowHeight(row, height)


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

    def selected_columns(self):
        return self.table.selectionModel().selectedColumns()

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def selected_indexes(self):
        indexes = self.table.selectionModel().selectedIndexes()
        if indexes:
            min_col = indexes[i.column()]
            max_col = indexes[i.column()]
            min_row = indexes[i.row()]
            max_row = indexes[i.row()]
            for i in self.table.selectionModel().selectedIndexes()[1:]:
                min_col = min(min_col, i.column())
                max_col = max(max_col, i.column())
                min_row = min(min_row, i.row())
                max_row = max(max_row, i.row())
            return  (
                (min_col,min_row),
                (max_col,max_row)
            )
        return ((None, None), (None, None))

    def get_sheet_statistics(self):
        print(self.count_rows())

    def count_rows(self):
        query = 'SELECT COUNT(1) as count FROM "base"'
        return self.db.simple_query(query)['count']

    def add_column(self, name=None):
        extra = name or "column__sam"
        # c = self.db_conn.cursor()
        # c.execute('''ALTER TABLE "base" ADD COLUMN ''' + extra + ''' INTEGER''')
        self.db.exec_('''ALTER TABLE "base" ADD COLUMN ''' + extra + ''' INTEGER''')

        self.tableModel.setTable('base')
        self.tableModel.select()
        # self.db_conn.commit()
