from PyQt5 import QtWidgets, QtCore, QtGui


class Button(QtWidgets.QPushButton):
    label = ""
    icon = None
    def __init__(self, *args, **kwargs):
        if self.icon:
            self._icon = QtGui.QIcon()
            self._icon.addFile(self.icon)
        else:
            self._icon = QtGui.QIcon()
        super().__init__(self._icon, self.label, *args, **kwargs)

        if self.icon:
            self.setIconSize(QtCore.QSize(20,20)) #self._icon.availableSizes()[0])
            self.setMinimumSize(QtCore.QSize(20,20))

        self.pressed.connect(self.action)

class HGroup(QtWidgets.QWidget):
    def __init__(self, actions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vbox = QtWidgets.QVBoxLayout()
        for action in actions:
            print(action)
            vbox.addWidget(action())
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(0)
        self.setLayout(vbox)

    def __call__(self):
        return self

class Group(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label')
        self.actions = kwargs.pop('actions')
        super().__init__(*args, **kwargs)
        self.setObjectName("toolbar_group")
        label = QtWidgets.QLabel(self.label)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        s = self.sizePolicy()
        s.setHorizontalPolicy(QtWidgets.QSizePolicy.Minimum)
        self.setSizePolicy(s)

        vbox = QtWidgets.QVBoxLayout()
        self.bit = QtWidgets.QWidget()

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        self.bit.setLayout(hbox)

        # # vbox.addWidget(self.menu)
        vbox.addWidget(self.bit)
        vbox.addWidget(label)
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(0)

        s = self.bit.sizePolicy()
        s.setVerticalPolicy(QtWidgets.QSizePolicy.Maximum)
        self.bit.setSizePolicy(s)

        self.setLayout(vbox)

        for opt in self.actions:
            hbox.addWidget(opt())


class ButtonWithDrop(QtWidgets.QWidget):
    icon = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        if self.icon:
            self._icon = QtGui.QIcon()
            self._icon.addFile(self.icon)
            self.top_label=""
        else:
            self._icon = QtGui.QIcon()
            self.top_label=self.label

        self.button = QtWidgets.QPushButton(self._icon, self.top_label)
        self.button.pressed.connect(self.action)

        if self.icon:
            self.button.setIconSize(QtCore.QSize(32,32)) #self._icon.availableSizes()[0])
            self.button.setMinimumSize(QtCore.QSize(32,32))
            s = self.button.sizePolicy()
            s.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
            self.button.setSizePolicy(s)

        self.menu_button = QtWidgets.QPushButton(self.label)
        menu = QtWidgets.QMenu(self.menu_button)
        for label, action in self.extra_actions:
            act = QtWidgets.QAction(label,self.menu_button)
            menu.addAction(act)
            if type(action) is str:
                action = getattr(self, action)
            act.triggered.connect(action)

        self.menu_button.setMenu(menu)
        vbox = QtWidgets.QVBoxLayout()

        # vbox.addWidget(self.toolbar)
        vbox.addWidget(self.button)
        vbox.addWidget(self.menu_button)
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(0)
        self.setLayout(vbox)

class TabToolbar(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hbox = QtWidgets.QHBoxLayout()

        for group in self.groups[::-1]:
            hbox.addWidget(group)

        hbox.insertStretch(0)
        hbox.setDirection(QtWidgets.QBoxLayout.RightToLeft)
        hbox.setContentsMargins(0,0,0,0)
        self.setLayout(hbox)
