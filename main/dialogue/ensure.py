# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtGui
from data.projects_manager import projectManager


class EnsureDialog(QtGui.QDialog):
    """Диалог для добавления проекта"""
    def __init__(self, root, parent=None, text=u'Вы уверены?',
                    title=u'Добавить поле'):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self, None)
        self.setWindowTitle(title)
        self.grid = QtGui.QGridLayout()

        btnAdd = QtGui.QPushButton(u'Ok')
        btnAdd.clicked.connect(self.accept)

        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)

        self.grid.addWidget(QtGui.QLabel(text), 0, 0)

        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(btnAdd)
        lt.addWidget(btnClose)

#        self.resize(400, 200)
        self.grid.addLayout(lt, 1, 0)
        self.setLayout(self.grid)
