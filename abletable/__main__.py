#!/usr/bin/env python
"""
AbleTable

Generate a dynamic Qt form representing a JSON Schema.
Filling the form will generate JSON.
"""

import sys

from PyQt5 import QtCore, QtGui, QtWidgets, QtSql

from.widgets.sheets import Sheet
from collections import OrderedDict

# from qtjsonschema.widgets import create_widget
app = QtWidgets.QApplication(sys.argv)

drivers = QtSql.QSqlDatabase.drivers()


class TabbableToolbar(QtWidgets.QTabWidget):
    pass


class TabToolbar(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(TabToolbar, self).__init__(*args, **kwargs)

class AbleTableToolbar(TabbableToolbar):
    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent')
        super(AbleTableToolbar, self).__init__(*args, **kwargs)
        self.setObjectName("ribbon")
        # self.setMaximumHeight(50)
        s = self.sizePolicy()
        s.setVerticalPolicy(QtWidgets.QSizePolicy.Minimum)
        self.setSizePolicy(s)

        from .toolbars.home import HomeToolbar
        from .toolbars.data import DataToolbar
        from .toolbars.view import ViewToolbar

        self.addTab(HomeToolbar(), HomeToolbar.title)
        self.addTab(DataToolbar(), DataToolbar.title)
        self.addTab(ViewToolbar(), ViewToolbar.title)

        self.set_menu()

    def set_menu(self):
        self.menu = QtWidgets.QMenuBar(self)

        menu = OrderedDict([
            ("&File", [
                ("&Open CSV", self.parent._handle_open),
                ("&Save select table", self.parent._handle_save),
                '--',
                ("&Close", self.parent._handle_quit),
            ]),
            # ("&Options", [
            #     ("Set theme", self.parent._handle_set_theme),
            # ])
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
        self.setCornerWidget(self.menu, QtCore.Qt.TopLeftCorner)

class AbleTableWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self,parent)
        self.center = QtWidgets.QWidget()
        self.toolbar = AbleTableToolbar(self, parent=self)

        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.what)

        vbox = QtWidgets.QVBoxLayout()
        # vbox.addWidget(self.menu)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.tabs)
        self.center.setLayout(vbox)

        self.setCentralWidget(self.center)
        self.setTitle("AbleTable")

        # self.set_menu()
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

    def current_sheet(self):
        return self.tabs.currentWidget()

    def all_sheets(self):
        return [
            self.tabs.widget(i)
            for i in range(self.tabs.count())
        ]

    def set_theme_from_resource(self):
        fd = QtCore.QFile(":/theme.css")
        if fd.open(QtCore.QIODevice.ReadOnly | QtCore.QFile.Text):
            text = QtCore.QTextStream(fd).readAll()
            self.setStyleSheet(text)

import click

@click.command()
@click.option('--csv', '-c', multiple=True, default=None, help='Schema file to generate an editing window from.')
@click.option('--theme', type=str, default=None, help='Schema file to generate an editing window from.')
def able_table(csv, theme): #schema, json):
    import sys, os
    
    print("theme", theme)
    if theme == "::res::":
        from .themes.excelsior import theme as _t
    from .themes.base import theme as _t

    main_window = AbleTableWindow()
    main_window.resize(800,600)

    # default theme

    main_window.show()
    for c in csv:
        main_window.add_sheet(c)
    if theme is not None:
        # main_window.do_it()
        print("setting theme", theme)
        if theme == "::res::":
            main_window.set_theme_from_resource()
        else:
            main_window.set_theme(theme)

    sys.exit(app.exec_())


if __name__ == "__main__":
    able_table()
