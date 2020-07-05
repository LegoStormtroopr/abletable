from PyQt5 import QtWidgets, QtCore
from .base import TabToolbar, ButtonWithDrop, Button, Group, HGroup



class ChangeTableFontComplex(ButtonWithDrop):
    label = "Change Font"
    icon = ":/action/preferences/font"
    extra_actions = [
        ("... for all tables", 'change_for_all'),
    ]

    def action(self):
        sheet = self.window().current_sheet()
        font, _ = QtWidgets.QFontDialog.getFont(self) #, 'Open CSV', filter="CSV File (*.csv *.tsv)")
        print(font)
        if font and sheet:
            sheet.setFont(font)

    def change_for_all(self):
        sheet = self.window().current_sheet()
        font, _ = QtWidgets.QFontDialog.getFont(self) #, 'Open CSV', filter="CSV File (*.csv *.tsv)")
        if font:
            for sheet in self.window().all_sheets():
                sheet.setFont(font)

class ChangeTableFont(Button):
    label = "Change Font"
    icon = ":/action/preferences/font"

    def action(self):
        font, _ = QtWidgets.QFontDialog.getFont(self)
        if font:
            for sheet in self.window().all_sheets():
                sheet.setFont(font)


class SplitView(Button):
    label = "Split view"
    icon = ":/action/preferences/font"

    def action(self):
        sheet = self.window().current_sheet()
        font, _ = QtWidgets.QFontDialog.getFont(self) #, 'Open CSV', filter="CSV File (*.csv *.tsv)")
        if font:
            self.window().current_sheet()
            sheet.setFont(font)


class ViewToolbar(TabToolbar):
    title = "View"
    groups = [
        Group(label="Font",
            actions = [
                ChangeTableFont,
            ]),
        Group(label="Layout",
            actions = [
                SplitView,
            ]),
    ]
