# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtGui
from data.projects_manager import projectManager


class FieldAddDialog(QtGui.QDialog):
    """Диалог для добавления проекта"""
    def __init__(self, root, parent=None):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self, None)

        self.setWindowTitle(u'Добавить поле')
        self.grid = QtGui.QGridLayout()

        if self.wrapper._kind == 'ddict':
            self._setupDD()
        elif self.wrapper._kind == 'list':
            self._setupSimple()
        else:
            self._setupHidden(list(self.wrapper._hiddenProp()))
           
        self._setupBase()
#        self.edtName.textChanged.connect(self._updateAddEnabled)

#        self.edtPath.setMinimumWidth(300)
#        self.edtPath.textChanged.connect(self._updateAddEnabled)

    def _setupDD(self):
        self.edtName = QtGui.QLineEdit()
        self.edtName.textChanged.connect(self.avaibility)
        self.grid.addWidget(QtGui.QLabel(u'имя поля:'), 0, 0)
        self.grid.addWidget(self.edtName, 0, 1)

    def _setupSimple(self):
        self.grid.addWidget(
            QtGui.QLabel(u'Добавить новое поле в список?'),
            0, 0, 1, 1
        )

    def _setupHidden(self, choices):
        self.edtName = QtGui.QComboBox()
        self.edtName.addItems(choices)
#        self.edtName.currentIndexChanged.connect(self.avaibility)
        self.grid.addWidget(QtGui.QLabel(u'имя поля:'), 0, 0)
        self.grid.addWidget(self.edtName, 0, 1)


    def _setupBase(self):
        self.btnAdd = QtGui.QPushButton(u'Подключить')
        self.btnAdd.setEnabled(False)
        self.btnAdd.clicked.connect(self._confirm)
#        self._updateAddEnabled('')
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)
        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(btnClose)

        self.grid.addLayout(lt, 3, 0, 1, 2)
        self.setLayout(self.grid)
        self.avaibility()
        
    def avaibility(self):
        if self.wrapper._kind in ('dict', 'list'):
            self.btnAdd.setEnabled(True)
            return

        field = '%s' % self.edtName.text().toUtf8()

        try:
            self.wrapper.wrapper.wrapper.doc.__check_add__(
                self.wrapper._addr, None, field
            )
            canAdd = True
        except:
            canAdd = False
            
        if field and canAdd:
            self.btnAdd.setEnabled(True)

    def _confirm(self):
        if self.wrapper._kind == 'ddict':
            self._field = '%s' % self.edtName.text().toUtf8()
        elif self.wrapper._kind == 'list':
            self._field = len(self.wrapper._data)
        else:
            self._field = '%s' % self.edtName.currentText().toUtf8()
        self.accept()
