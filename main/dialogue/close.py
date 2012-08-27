# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtGui


class CloseDialog(QtGui.QDialog):
    """Диалог для добавления проекта"""
    def __init__(self, root, parent=None, text=u'Имеются несохраненные изменения, вы уверены что хотите выйти?',
                    title=u'Выход'):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.grid = QtGui.QGridLayout()
        self._save = False

        btnAdd = QtGui.QPushButton(u'Сохранить и выйти')
        btnAdd.clicked.connect(self._accept)

        btnIgnore = QtGui.QPushButton(u'Выйти без сохранения')
        btnIgnore.clicked.connect(self.accept)

        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)

        self.grid.addWidget(QtGui.QLabel(text), 0, 0)

        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(btnAdd)
        lt.addWidget(btnIgnore)
        lt.addWidget(btnClose)

#        self.resize(400, 200)
        self.grid.addLayout(lt, 1, 0)
        self.setLayout(self.grid)

    def _accept(self):
        self._save = True
        self.accept()