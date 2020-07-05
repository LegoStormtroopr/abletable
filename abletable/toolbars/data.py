from PyQt5 import QtWidgets, QtCore
from .base import TabToolbar, ButtonWithDrop, Button, Group, HGroup


class RemoveDuplicates(Button):
    label = "Remove\nDuplicates"
    icon = ":/toolbars/home/cut"

    def action(self):
        sheet = self.window().current_sheet()
        before = sheet.count_rows()
        print("Before", before)

        if sheet.selected_columns():
            selected = sheet.selected_columns()[0]
            # db_col = sheet.tableModel.headerData(selected.column(), QtCore.Qt.Horizontal)
            db_col = "\",\"".join([
                sheet.tableModel.headerData(col.column(), QtCore.Qt.Horizontal)
                for col in sheet.selected_columns()
            ])
            print(db_col)
            query = """
                DELETE FROM base
                WHERE rowid NOT IN (
                  SELECT MIN(rowid) 
                  FROM base 
                  GROUP BY {cols}
                )
            """.format(cols=db_col)
            for i in sheet.db.multirow_query(query):
                print(i)

        sheet.tableModel.select()
        after = sheet.count_rows()
        print("After", after)
        print("Removed", before - after)


class Distinct(Button):
    label = "Distinct"
    icon = ":/action/search/find"

    def action(self):
        sheet = self.window().current_sheet()

        if sheet.selected_columns():
            selected = sheet.selected_columns()[0]
            # db_col = sheet.tableModel.headerData(selected.column(), QtCore.Qt.Horizontal)
            db_col = "\",\"".join([
                sheet.tableModel.headerData(col.column(), QtCore.Qt.Horizontal)
                for col in sheet.selected_columns()
            ])
            print(db_col)
            query = """
                select distinct "{cols}", count() as count
                 from 'base'
                 group by "{cols}";
            """.format(cols=db_col)
            for i in sheet.db.multirow_query(query):
                print(i)
            # print(list(sheet.db.multirow_query(query)))
        print(sheet.table.selectionModel().selectedColumns())
        # print(sheet.db.simple_query(query))


class Sum(Button):
    label = "Sum"
    icon = ":/toolbars/home/copy"

    def action(self):
        sheet = self.window().current_sheet()

        if sheet.selected_columns():
            selected = sheet.selected_columns()[0]
            db_col = sheet.tableModel.headerData(selected.column(), QtCore.Qt.Horizontal)
            query = """select sum("{col}") as sum from 'base'""".format(col=db_col)
            print(list(sheet.db.multirow_query(query)))
        print(sheet.selected_columns())
        print(sheet.selected_rows())
        print(sheet.selected_indexes())


class DataToolbar(TabToolbar):
    title = "Data"
    groups = [
        Group(label="Sort & filter",
            actions = [
                Sum,
                Distinct,
                RemoveDuplicates,
            ]),
    ]
