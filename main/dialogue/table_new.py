# coding: utf-8
"""Модуль добавления проекта"""
import re
from PyQt4 import QtGui
from data.projects_manager import projectManager
from main.base.selectBox import QSelectBox

class TableNewDialugue(QtGui.QDialog):
    """Диалог для добавления проекта"""
    def __init__(self, root, treeitem, parent=None):
        self.root = root
        self.wrapper = parent
        self.treeitem = treeitem
        QtGui.QDialog.__init__(self)

        self.setWindowTitle(u'Добавить таблицу')
        self.grid = QtGui.QGridLayout()

        self.edtName = QtGui.QLineEdit()
        self.edtName.textChanged.connect(self.avaibility)

        self.edtType = QSelectBox()
        self.edtType.standart()
#        self.edtType.currentIndexChanged.connect(self._typeChenged)

#        self.edtPath.setMinimumWidth(300)
#        self.edtPath.textChanged.connect(self._updateAddEnabled)

        

        self.grid.addWidget(QtGui.QLabel(u'имя таблицы:'), 0, 0)
        self.grid.addWidget(self.edtName, 0, 1)

        self.grid.addWidget(QtGui.QLabel(u'динамичный:'), 1, 0)
        self.grid.addWidget(self.edtType, 1, 1)


        self.btnAdd = QtGui.QPushButton(u'Ок')
        self.btnAdd.setEnabled(False)
        self.btnAdd.clicked.connect(self._confirm)
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)

        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(btnClose)

        self.grid.addLayout(lt, 2, 0, 1, 2)
        self.setLayout(self.grid)

    def avaibility(self):
        name = '%s' % self.edtName.text()
        if not name or name in self.treeitem._project.data.table \
        or not re.match("[A-Za-z0-9]", name):
            self.btnAdd.setEnabled(False)
        else:
            self.btnAdd.setEnabled(True)

    def _confirm(self):
        self._name = '%s' % self.edtName.text()
        self._kwargs = {}
        index = self.edtType.currentIndex()
        if self.edtType.itemData(index).toPyObject():
            self._kwargs['dynamic'] = 1

        self.accept()
