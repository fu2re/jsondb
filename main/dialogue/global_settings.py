# coding: utf-8
import hashlib
import re
from PyQt4 import QtGui
from data.projects_manager import projectManager
#from main.base.selectBox import QSelectBox

class SettingsDialugue(QtGui.QDialog):
    """
    Диалог глобальных настроек
    """
    def __init__(self, root, parent=None):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self)

        self.setWindowTitle(u'Настройки')
        self.grid = QtGui.QGridLayout()
        ltF = QtGui.QFormLayout()

        self.remoteServer = QtGui.QLineEdit(
            self.root.window.settings.value("acc/remote").toPyObject()
        )
        ltF.addRow(u'Адрес статического сервера:', self.remoteServer)

        self.ACCPassword = QtGui.QLineEdit(
            self.root.window.settings.value("acc/key").toPyObject()
        )
        self.ACCPassword.setEchoMode(QtGui.QLineEdit.Password)
        ltF.addRow(u'Пароль:', self.ACCPassword)

        self.ACCHome = QtGui.QLineEdit(
            self.root.window.settings.value("acc/home").toPyObject()
        )
        btnPath = QtGui.QToolButton()
        btnPath.setText(u'...')
        btnPath.clicked.connect(self.__updatePath)

        ltPath = QtGui.QHBoxLayout()
        ltPath.setContentsMargins(0, 0, 0, 0)
        ltPath.addWidget(self.ACCHome)
        ltPath.addWidget(btnPath)

        ltF.addRow(u'Домашняя папка', ltPath)

        self.btnAdd = QtGui.QPushButton(u'Ок')
        self.btnAdd.clicked.connect(self._confirm)
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)

        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(btnClose)

        self.grid.addLayout(ltF, 1, 0)
        self.grid.addLayout(lt, 2, 0)
        self.setLayout(self.grid)


    def _confirm(self):
        _ACC_key = '%s' % self.ACCPassword.text()
        _ACC_Remote = re.sub('http://', '', '%s' % self.remoteServer.text())
        self.root.window.settings.setValue('acc/key', _ACC_key)
        self.root.window.settings.setValue('acc/remote', _ACC_Remote)
        self.root.window.settings.setValue('acc/home', '%s' % self.ACCHome.text())
        projectManager.update(_ACC_key, _ACC_Remote)
    
        self.accept()
        
    def a(self, a):
        self.pth = a

    def __updatePath(self):
        """
        Открывает диалог выбора директории и обновляет путь
        """
        directory = QtGui.QFileDialog(
            self,
            u'Выберите директорию:',
            self.ACCHome.text()
        )
        directory.setOption(QtGui.QFileDialog.ShowDirsOnly)
        directory.setFileMode(QtGui.QFileDialog.Directory)
        directory.fileSelected.connect(self.a)
        directory.exec_()
        if self.pth:
            self.ACCHome.setText(self.pth)