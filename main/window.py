# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtCore, QtGui, Qt
from main.dialogue.close import CloseDialog

class uni(object):
    settings = QtCore.QSettings('JsonDBExplorer', 'Window')

    def _to_utf(self, text):
        """
        Перевод строки в юникод
        """
        return QtGui.QApplication.translate(
            "MainWindow",
            text,
            None,
            QtGui.QApplication.UnicodeUTF8
        )

class QMainWindow(QtGui.QMainWindow, uni):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.cpanel = QtGui.QSplitter(self)
        self.main = QtGui.QSplitter(QtCore.Qt.Vertical)        
        self.setCentralWidget(self.main)
        self.act = QtGui.QPlainTextEdit()
        self.act.setReadOnly(True)
        self.act.setMaximumHeight(200)
        self.main.addWidget(self.cpanel)
        self.main.addWidget(self.act)
        self.menubar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.save = QtGui.QLabel()
        self.statusbar.save.setPixmap(QtGui.QPixmap(os.path.join("ui", "save.png")))
        self.statusbar.save.setVisible(False)
        self.statusbar.addPermanentWidget(self.statusbar.save)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('ready')

#        self.grid = QtGui.QGridLayout()
        self.setGeometry(self.settings.value('geometry', QtCore.QRect(300, 300, 410, 120)).toRect())


    def closeEvent(self, event):
        """
        Перезаписываем событие при закрытии
        Сохраняем состояния объектов и геометрию, открыте вкладки и тд
        """
        dialog = CloseDialog(self.root, self)
        if not self.root.changed or dialog.exec_() == QtGui.QDialog.Accepted:
            if dialog._save:
                self.root._save()

            self.settings.setValue('geometry', QtCore.QVariant(self.geometry()))
            self.settings.setValue("main/state/v", self.main.saveState())
            self.settings.setValue("main/state/h", self.cpanel.saveState())

            # TODO открыте вкладки и тд
            super(QMainWindow, self).closeEvent(event)

    def _build_menu(self, name, args):
        """
        Сторим меню из аргумента
        """
        menu = self.menubar.addMenu(self._to_utf(name))
        for i in args:
            action, function, shortcut = i
            item = QtGui.QAction(self.main)
            item.setText(self._to_utf(action))

            if shortcut:
                item.setShortcut(shortcut)

            self.connect(item, QtCore.SIGNAL('triggered()'), function)
            menu.addAction(item)

    def _on_exit(self):
#        settings = QtCore.QSettings("MyCompany", "MyApp")
        print QtCore.QVariant(self.geometry())


    def _set_title(self, name):
        """
        Устанавливаем имя окна
        """
        self.setWindowTitle(self._to_utf(name))


