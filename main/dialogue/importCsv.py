# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtCore, QtGui
from data.projects_manager import projectManager


class ImportDialog(QtGui.QDialog):
    """
    Диалог для иппорта из csv
    """
    def __init__(self, root, parent=None):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self, None)
#        self.resize(400,400)
        self.setWindowTitle(u'Импортировать CSV')
        self.grid = QtGui.QGridLayout()
        self._sync = False

        self.edtPath = QtGui.QLineEdit()
        self.edtPath.setMinimumWidth(300)
        self.edtPath.textChanged.connect(self.avaibility)

        self.sync = QtGui.QCheckBox()
        ltSync = QtGui.QHBoxLayout()
        ltSync.setContentsMargins(0, 0, 0, 0)
        ltSync.addWidget(self.sync)
        ltSync.addWidget(QtGui.QLabel(u'Удалить документы которых нет в таблице'))
        self.grid.addLayout(ltSync, 0, 0)

        btnPath = QtGui.QToolButton()
        btnPath.setText(u'...')
        btnPath.clicked.connect(self.__updatePath)

        ltPath = QtGui.QHBoxLayout()
        ltPath.setContentsMargins(0, 0, 0, 0)
        ltPath.addWidget(self.edtPath)
        ltPath.addWidget(btnPath)

        self.grid.addLayout(ltPath, 1, 0)
        self._setupBase()

    def _setupBase(self):
        self.btnAdd = QtGui.QPushButton(u'Ок')
        self.btnAdd.setEnabled(False)
        self.btnAdd.clicked.connect(self._confirm)
#        self._updateAddEnabled('')
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)
        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(btnClose)

        self.grid.addLayout(lt, 2, 0)
        self.setLayout(self.grid)
        self.avaibility()

    def avaibility(self):
        self.btnAdd.setEnabled(
            bool(self.edtPath.text())
        )

    def _confirm(self):
        self._pth = '%s' % self.edtPath.text()
        self.accept()


    def a(self, a):
        self.pth = a

    def __updatePath(self):
        """
        Открывает диалог выбора директории и обновляет путь
        """
        directory = QtGui.QFileDialog(
            self,
            u'Выберите директорию проекта:',
            self.edtPath.text()
        )
#        directory.setOption(QtGui.QFileDialog.ShowDirsOnly)
        directory.setFileMode(QtGui.QFileDialog.ExistingFile)
        directory.setFilter('*.csv')
        directory.fileSelected.connect(self.a)
        directory.exec_()
        if self.pth:
            self.edtPath.setText(self.pth)