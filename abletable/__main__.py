#!/usr/bin/env python
"""
AbleTable

Generate a dynamic Qt form representing a JSON Schema.
Filling the form will generate JSON.
"""

import sys

from PyQt5 import QtCore, QtGui, QtWidgets, QtSql

from.widgets import Sheet
from collections import OrderedDict

# from qtjsonschema.widgets import create_widget
app = QtWidgets.QApplication(sys.argv)

drivers = QtSql.QSqlDatabase.drivers()


class Database(QtSql.QSqlDatabase) :
    def __init__(self, *args):
        super(Database,  self).__init__(*args)

        self.addDatabase("QSQLITE")
        self.setDatabaseName(':memory:')
        if not self.open():
            QtWidgets.QMessageBox.critical(None, QtWidgets.qApp.tr("Cannot open database"),
                QtWidgets.qApp.tr("Unable to establish a database connection.\n"
                "This example needs SQLite support. Please read "
                "the Qt SQL driver documentation for information "
                "how to build it.\n\n" "Click Cancel to exit."),
             QtWidgets.QMessageBox.Cancel)
                
        return False  


class AbleTableWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self,parent)
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.what)
        self.sheets = []
        
        self.setCentralWidget(self.tabs)
        self.setTitle("AbleTable")

        self.set_menu()
        self.statusBar().showMessage('Ready')


    def set_menu(self):
        self.menu = self.menuBar()

        menu = OrderedDict([
            ("&File", [
                ("&Open CSV", self._handle_open),
                ("&Save select table", self._handle_save),
                '--',
                ("&Close", self._handle_quit),
            ]),
            ("&Options", [
                ("Set theme", self._handle_set_theme),
            ])
        ])
        self.actions = []
        for title, sub in menu.items():
            sub_menu = self.menu.addMenu(title)
            for sub_title, action in sub:
                if sub_title[0] == "-":
                    sub_menu.addSeparator()
                    continue
                _action = QtWidgets.QAction(sub_title, self)
                _action.triggered.connect(action)

                sub_menu.addAction(_action)


    def _handle_save(self):
        self.tabs.currentWidget().save_csv()

    def _handle_open(self):
        # Open JSON Schema
        csv_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open CSV', filter="CSV File (*.csv *.tsv)")
        if csv_file:
            self.add_sheet(csv_file)

    def _handle_quit(self):
        # TODO: Check if saved?
        self.close()

    def what(self, index):
        print("want to close %s"%index)
        self.tabs.removeTab(index)

    def setTitle(self, title):
        self.setWindowTitle("AbleTable - {}".format(title))

    def add_sheet(self, csv):
        sheet = Sheet(parent=self.tabs)
        # self.sheets.append(sheet)
        self.tabs.addTab(sheet, "")
        sheet.open_csv(csv)


    def _handle_set_theme(self):
        # Open JSON Schema
        theme_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Theme', filter="Theme File (*.css)")
        if theme_file:
            self.set_theme(theme_file)

    def set_theme(self, theme):
        with open(theme) as t:
            self.setStyleSheet(t.read())


import click

@click.command()
@click.option('--csv', '-c', multiple=True, default=None, help='Schema file to generate an editing window from.')
@click.option('--theme', type=str, default=None, help='Schema file to generate an editing window from.')
def able_table(csv, theme): #schema, json):
    import sys, os
    
    print("theme", theme)
    main_window = AbleTableWindow()
    main_window.resize(800,600)

    main_window.show()
    for c in csv:
        main_window.add_sheet(c)
    if theme:
        # main_window.do_it()
        print("setting theme", theme)
        main_window.set_theme(theme)

    sys.exit(app.exec_())


if __name__ == "__main__":
    able_table()
