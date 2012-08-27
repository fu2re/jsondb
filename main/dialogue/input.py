# coding: utf-8
from PyQt4 import QtGui
from data.projects_manager import projectManager
#from main.base.selectBox import QSelectBox

class InputDialugue(QtGui.QDialog):
    """
    Диалог глобальных настроек
    """
    def __init__(self, root, parent=None, text='', initial=''):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self, None)
        self.setWindowTitle(text)
        self.grid = QtGui.QGridLayout()
        
        self.edtPath = QtGui.QLineEdit(initial)
        self.edtPath.setMinimumWidth(300)

        self.grid.addWidget(self.edtPath, 0, 0)
        self.btnAdd = QtGui.QPushButton(u'Ок')
        self.btnAdd.clicked.connect(self._confirm)
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)

        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(btnClose)

        self.grid.addLayout(lt, 3, 0, 1, 2)
        self.setLayout(self.grid)
    

    def _confirm(self):
        self._val = '%s' % self.edtPath.text()
        self.accept()
