# coding: utf-8
"""Модуль добавления проекта"""
import os.path

from PyQt4 import QtCore, QtGui
import os
import sys
import json
import traceback
from __step__ import Step
from __resizable__ import Resizable

class AMFDialog(Step, Resizable):
    """
    Диалог выполнения пользовательского скрипта
    """
    def __init__(self, root, project):
        self.currentStep = self.__tables
        self.steps = (
            self.__tables,
            self.__mode,
            self.__params,
            self.__result
        )
        self.root = root
        self.project = project.data
        self.project_name = project.name

        Step.__init__(self)
        self.setWindowTitle(u'"Экспорт в AMF')
        self._fill()
        self.currentStep()
        self._restoreGeom('dialog/amf/geometry', 800, 300)

    def _fill(self):
        self.list = QtGui.QListView(self)
        self.model = QtGui.QStandardItemModel()
        tables =  self.project.table.keys()
        checked = [k for k,v in self.project.table.items() if v.__field__('').compressed]
        for i in tables:
            item = QtGui.QStandardItem(i) #QCheckBox(i, self)
            check = QtCore.Qt.Checked if i in checked else QtCore.Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            self.model.appendRow(item)
        self.list.setModel(self.model)

        lt = QtGui.QVBoxLayout()
        self.radio = QtGui.QGroupBox()
        self.optsv = QtGui.QRadioButton(u'Сохранить на диск')
        self.optsv.setChecked(True)
        self.optup = QtGui.QRadioButton(u'Закачать на сервер')
        lt.addWidget(self.optsv)
        lt.addWidget(self.optup)
        lt.addStretch(1)
        self.radio.setLayout(lt)

        self.edtName = QtGui.QLineEdit('balance.amf')
        self.edtName.setMinimumWidth(300)
        self.edtName.textChanged.connect(self.avaibility)
        self.edtPath = QtGui.QLineEdit(
            self.root.window.settings.value("acc/home").toPyObject()
        )
        self.edtPath.setMinimumWidth(300)
        self.edtPath.textChanged.connect(self.avaibility)
        self.btnPath = QtGui.QToolButton()
        self.btnPath.setText(u'...')
        self.btnPath.clicked.connect(self.__updatePath)
        self.edtTag = QtGui.QLineEdit('balance, %s' % self.project.summary()[0])


    def __tables(self):
        self._clear(True)
        self._addLayout('', self.list)
        self.btnGo.setEnabled(True)

    def __mode(self):
        self._clear()        
        self._addLayout('', self.radio)

    def __params(self):
        self._clear()        
        self.amf_fields = []
        while True:
            item = self.model.takeRow(0)
            if not item:
                break

            if item[0].checkState() == 2:
                self.amf_fields.append('%s' % item[0].text())        

        if self.optsv.isChecked():
            self._addLayout(u'Имя файла', self.edtName)
            self._addLayout(u'Путь', self.edtPath)
            self._addLayout(u'Обзор', self.btnPath)
        else:
            self._addLayout(u'Теги', self.edtTag)
        self.avaibility()
        
    def __result(self):
        self._clear()
        self.__block__()
        path = os.path.join(
            '%s' % self.edtPath.text(), '%s' % self.edtName.text()
        ) if self.optsv.isChecked() else None
        try:
            response = self.project.amf(
                self.amf_fields,
                path=path,
                upload=bool(self.optup.isChecked()),
                tags='%s' % self.edtTag.text()
            )
            self._show(
                u'Файл создан: %s' % os.path.abspath(path) if not response
                else u'Ответ: %s' % json.dumps(json.loads(response), indent=4)
            )
        except:
             self._show(traceback.format_exc())
        
        self.__finish__()

    def avaibility(self):
        if self.optup.isChecked():
            self.btnGo.setEnabled(True)
        else:
            self.btnGo.setEnabled(
                bool(self.edtPath.text() and self.edtName.text())
            )

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
        directory.setOption(QtGui.QFileDialog.ShowDirsOnly)
        directory.setFileMode(QtGui.QFileDialog.Directory)
        directory.fileSelected.connect(self.a)
        directory.exec_()
        if self.pth:
            self.edtPath.setText(self.pth)

