# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtCore, QtGui
from data.projects_manager import projectManager


class ExportDialog(QtGui.QDialog):
    """Диалог для добавления проекта"""
    def __init__(self, root, parent=None):
        self.root = root
        self.wrapper = parent
        QtGui.QDialog.__init__(self, None)
        self.resize(400,400)
        self.setWindowTitle(u'Экспортировать CSV')
        self.grid = QtGui.QGridLayout()
        self.list = QtGui.QListView(self)
        self.model = QtGui.QStandardItemModel()
        fields = self.root.window.settings.value(
            "project/%s/%s/visible" % (self.wrapper._project.name, self.wrapper._table.name),
            ()
#            self.wrapper.table.simple_fields()
        ).toPyObject()

        self._vfields = ['id']
        self._vfields.extend(fields or [])
        self._fill(custom=True)
        self.list.setModel(self.model)
        self.grid.addWidget(self.list, 0, 0)

        self.edtName = QtGui.QLineEdit(
        '%s_%s' % (self.wrapper._table.name, self.wrapper._project.data.summary()[1])
        )
        self.edtName.setMinimumWidth(200)
        self.edtPath = QtGui.QLineEdit(
            self.root.window.settings.value("acc/home").toPyObject()
        )
        self.edtPath.setMinimumWidth(300)
        self.edtPath.textChanged.connect(self.avaibility)

        btnPath = QtGui.QToolButton()
        btnPath.setText(u'...')
        btnPath.clicked.connect(self.__updatePath)

        ltPath = QtGui.QHBoxLayout()
        ltPath.setContentsMargins(0, 0, 0, 0)
        ltPath.addWidget(QtGui.QLabel())
        ltPath.addWidget(self.edtPath)
        ltPath.addWidget(btnPath)

        ltF = QtGui.QFormLayout()
        ltF.addRow(u'Имя файла', self.edtName)
        ltF.addRow(u'Путь', ltPath)

        self.grid.addLayout(ltF, 1, 0)
        self._setupBase()
        
    def _setupBase(self):
        self.btnAdd = QtGui.QPushButton(u'Ок')
        self.btnAdd.setEnabled(False)
        self.btnAdd.clicked.connect(self._confirm)
        uall = QtGui.QPushButton(u'Очистить все')
        uall.clicked.connect(self._ufill)
        sall = QtGui.QPushButton(u'Выделить все')
        sall.clicked.connect(self._afill)
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)
        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(sall)
        lt.addWidget(uall)
        lt.addWidget(btnClose)

        self.grid.addLayout(lt, 2, 0)
        self.setLayout(self.grid)
        self.avaibility()

    def avaibility(self):
        self.btnAdd.setEnabled(
            bool(self.edtName.text() and self.edtPath.text())
        )

    def _confirm(self):
        self._fields = []
        self._pth = '%s' % self.edtPath.text()
        while True:
            item = self.model.takeRow(0)
            if not item:
                return self.accept()

            if item[0].checkState() == 2:
                self._fields.append('%s' % item[0].text())

    def a(self, a):
        self.pth = a

    def _ufill(self):
        self._fill(QtCore.Qt.Unchecked)

    def _afill(self):
        self._fill(QtCore.Qt.Checked)

    def _fill(self, state=QtCore.Qt.Checked, custom=False):
        fields = self.wrapper._table.simple_fields()
        self.model.clear()
        for i in fields:
            if i != '':
                item = QtGui.QStandardItem(i) #QCheckBox(i, self)
                if custom:
                    state = QtCore.Qt.Checked if i in self._vfields else QtCore.Qt.Unchecked
                item.setCheckState(state)
                item.setCheckable(True)
                self.model.appendRow(item)

#            self.grid.addRow(cbox)
        


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