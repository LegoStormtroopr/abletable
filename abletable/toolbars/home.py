from PyQt5 import QtWidgets
from .base import TabToolbar, ButtonWithDrop, Button, Group, HGroup

class Paste(ButtonWithDrop):
    label = "Paste"
    icon = ":/action/edit/paste"

    def action(self):
        print("hello")

    def paste_special(self):
        print("dsafsdfsdf")

    def text_import_wizard(self):
        print(self, "dsafsdfsdf")

    extra_actions = [
        ("Text import wizard", 'text_import_wizard'),
        ("Paste Special", 'paste_special')
    ]

class Cut(Button):
    label = "Cut"
    icon = ":/action/edit/cut"

    def action(self):
        print("hello")
        print(self.window().current_sheet())


class Copy(Button):
    label = "Copy"
    icon = ":/action/edit/copy"

    def action(self):
        pass


class HomeToolbar(TabToolbar):
    title = "Home"
    groups = [
        Group(label="Clipboard",
            actions = [
                Paste,
                HGroup([Cut, Copy,])
            ]),
    ]
