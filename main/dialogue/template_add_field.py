# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtGui
from data.projects_manager import projectManager


class FieldAddDialog(QtGui.QDialog):
    """Диалог для добавления проекта"""
    def __init__(self, root, parent=None):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self, root.window)

        self.setWindowTitle(u'Добавить поле')
        self.grid = QtGui.QGridLayout()

        self.edtName = QtGui.QLineEdit()
        self.edtName.textChanged.connect(self.avaibility)
#        self.edtName.textChanged.connect(self._updateAddEnabled)
        self.edtDef = QtGui.QLineEdit()
        self.edtDef.textChanged.connect(self.avaibility)

        self.edtType = QtGui.QComboBox()        
        self.edtType.addItems(projectManager.pattern.keys())
        self.edtType.currentIndexChanged.connect(self._typeChenged)

#        self.edtPath.setMinimumWidth(300)
#        self.edtPath.textChanged.connect(self._updateAddEnabled)

        self.btnAdd = QtGui.QPushButton(u'Подключить')
        self.btnAdd.setEnabled(False)
        self.btnAdd.clicked.connect(self._confirm)

#        self._updateAddEnabled('')
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)

        self.grid.addWidget(QtGui.QLabel(u'имя поля:'), 0, 0)
        self.grid.addWidget(self.edtName, 0, 1)

        self.grid.addWidget(QtGui.QLabel(u'Тип:'), 1, 0)
        self.grid.addWidget(self.edtType, 1, 1)

        self.grid.addWidget(QtGui.QLabel(u'Значение по умолчанию:'), 2, 0)
        self.grid.addWidget(self.edtDef, 2, 1)


        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(btnClose)

        self.grid.addLayout(lt, 3, 0, 1, 2)
        self.setLayout(self.grid)

    def avaibility(self):
        addr = self.wrapper.wrapper.wrapper._getaddr(
            self.wrapper._addr,
            '%s' % self.edtName.text()
        )
        if not self.edtName.text() or \
        self.wrapper.wrapper.wrapper.table.exist(addr):
            self.btnAdd.setEnabled(False)

        elif not self.edtDef.isEnabled():
            self.btnAdd.setEnabled(True)

        else:
            val = '%s' % self.edtDef.text().toUtf8()
            t = '%s' % self.edtType.currentText().toUtf8()
            try:
                projectManager.converter[t](val)
                self.btnAdd.setEnabled(True)
            except:
                self.btnAdd.setEnabled(False)

    def _typeChenged(self):
        t = '%s' % self.edtType.currentText()
        if t in ('list', 'dict', 'dynamic dict'):
            self.edtDef.setEnabled(False)
        else:
            if not self.edtDef.text():
                self.edtDef.setText(
                    str(self.wrapper.wrapper.wrapper.table.core.defaults[t])
                )
            self.edtDef.setEnabled(True)
        self.avaibility()

    def _confirm(self):
        self._name = '%s' % self.edtName.text().toUtf8()
        self._kwargs = {}
        self._kind = '%s' % self.edtType.currentText().toUtf8()
        if self._kind == 'dynamic dict':
            self._kind = 'dict'
            self._kwargs['dynamic'] = 1

        if self._kind not in ('list', 'dict'):
            self._kwargs['default'] = projectManager.converter[self._kind](
                '%s' % self.edtDef.text().toUtf8()
            )

        self.accept()
