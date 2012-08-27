# coding: utf-8
import os
import re
import shutil
from PyQt4 import QtGui
#from main.base.selectBox import QSelectBox
from __resizable__ import Resizable

class ProjectProperty(QtGui.QDialog, Resizable):
    """
    Диалог глобальных настроек
    """
    def __init__(self, root, project):
        self.root = root
        self.project = project
        QtGui.QDialog.__init__(self)

        self.main = QtGui.QTabWidget(self)

        self.setWindowTitle(u'Настройки проекта')
        self.grid = QtGui.QGridLayout()

        self.main.addTab(self._NetProp(), u'Сеть')
        self.main.addTab(self._PluginProp(), u'Плагины')
        self.grid.addWidget(self.main, 0, 0)



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
        self._restoreGeom('dialog/projectprop/geometry', 400, 400)

    def _NetProp(self):
        w = QtGui.QWidget()
        wl = QtGui.QFormLayout()
        self.project_name = QtGui.QLineEdit(
            self.root.window.settings.value(
                "proj/%s/name" % self.project.name, self.project.name
            ).toPyObject()
        )
        wl.addRow(u'Папка на удаленном сервере:', self.project_name)
        w.setLayout(wl)
        return w

    def _PluginProp(self):
        w = QtGui.QWidget()
        wl = QtGui.QHBoxLayout()
        self.plugins = QtGui.QListWidget()
        self.plugins._pth = os.path.abspath(os.path.join(
            self.project.data.path, 'scripts'
        ))
        self._fill()
        self.plugins.itemClicked.connect(self._PluginAvaibility)
        wl.addWidget(self.plugins)
        
        btnAdd = QtGui.QPushButton(u'Добавить')
        self.btnDel = QtGui.QPushButton(u'Удалить')
        btnAdd.clicked.connect(self.__updatePath)
        self.btnDel.clicked.connect(self._PluginDel)
        pl = QtGui.QFormLayout()
        pl.addRow(btnAdd)
        pl.addRow(self.btnDel)

        wl.addLayout(pl)
        w.setLayout(wl)
        self._PluginAvaibility()
        return w

    def _PluginAvaibility(self):
        self.btnDel.setEnabled(bool(self.plugins.currentItem()))

    def _fill(self):
        self.plugins.clear()
        plugins = os.listdir(self.plugins._pth)
        for i in plugins:
            if not re.search('.swf$', i):
                continue
            self.plugins.addItem(i)

    def _PluginDel(self):
        plugin = '%s' % self.plugins.currentItem().text()
        os.remove(os.path.join(self.plugins._pth, plugin))
        self._fill()

    def _PluginAdd(self, path):
        shutil.copy('%s' % path, self.plugins._pth)
        self._fill()

    def _confirm(self):
        remoteFolder = '%s' % self.project_name.text()
        self.root.window.settings.setValue(
            "proj/%s/name" % self.project.name,
            remoteFolder
        )
        try:
            self.project.data.project_name = remoteFolder
        except:
            pass
        self.accept()

    def a(self, a):
        self.pth = a

    def __updatePath(self):
        """
        Открывает диалог выбора директории и обновляет путь
        """
        directory = QtGui.QFileDialog(
            self,
            u'Выберите Файл:',
            ''
        )
#        directory.setOption(QtGui.QFileDialog.ShowDirsOnly)
        directory.setFileMode(QtGui.QFileDialog.ExistingFile)
#        directory.setFilter('*.swf')
        directory.fileSelected.connect(self._PluginAdd)
        directory.exec_()