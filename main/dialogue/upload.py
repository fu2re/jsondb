# coding: utf-8
import sys
import traceback
from PyQt4 import QtGui
import json

class UploadDialugue(QtGui.QDialog):
    """
    Диалог глобальных настроек
    """
    def __init__(self, root, parent=None, item=None):
        self.root = root
        self.wrapper = parent
        self.item = item
        QtGui.QDialog.__init__(self, None)
        self.setWindowTitle(u'Загрузить файл')
        self.grid = QtGui.QGridLayout()

        self.tags = QtGui.QLineEdit(self.wrapper.wrapper.table.name)
        self.grid.addWidget(QtGui.QLabel(u'Теги:'), 0, 0)
        self.grid.addWidget(self.tags, 0, 1)

        self.edtPath = QtGui.QLineEdit()
        self.edtPath.setMinimumWidth(300)
        self.edtPath.textChanged.connect(self.avaibility)

        btnPath = QtGui.QToolButton()
        btnPath.setText(u'...')
        btnPath.clicked.connect(self.__updatePath)

        ltPath = QtGui.QHBoxLayout()
        ltPath.setContentsMargins(0, 0, 0, 0)
        ltPath.addWidget(self.edtPath)
        ltPath.addWidget(btnPath)

        self.grid.addWidget(QtGui.QLabel(u'Файл:'), 1, 0)
        self.grid.addLayout(ltPath, 1, 1)
        
        self.btnAdd = QtGui.QPushButton(u'Ок')
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
        self.btnAdd.setEnabled(
            bool(self.edtPath.text())
        )

    def _confirm(self):
        try:
            self.root.window.statusbar.showMessage("Uploading...")
            self._resp = json.loads(
                self.wrapper.wrapper.table.core.wrapper.upload(
                    '%s' % self.edtPath.text(),
                    '%s' % self.tags.text()
                )
            )
        except:
            self.root._log(
                str(sys.exc_info()[1]),
                traceback.format_exc()
            )
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
        directory.fileSelected.connect(self.a)
        directory.exec_()
        if self.pth:
            self.edtPath.setText(self.pth)
