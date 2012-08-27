# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtGui
from data.projects_manager import projectManager


class ProjectAddDialog(QtGui.QDialog):
	"""Диалог для добавления проекта"""

	def __init__(self, parent=None):
		super(ProjectAddDialog, self).__init__(parent)
		self.setWindowTitle(u'Подключение проекта')
                self.pth = None
		mainLt = QtGui.QGridLayout()
		self.edtName = QtGui.QLineEdit()
		self.edtName.textChanged.connect(self._updateAddEnabled)
		self.edtPath = QtGui.QLineEdit()
		self.edtPath.setMinimumWidth(300)
		self.edtPath.textChanged.connect(self._updateAddEnabled)
		btnPath = QtGui.QToolButton()
		btnPath.setText(u'...')
		btnPath.clicked.connect(self.__updatePath)
		self.btnAdd = QtGui.QPushButton(u'Подключить')
		self.btnAdd.clicked.connect(self._addProject)
		self._updateAddEnabled('')
		btnClose = QtGui.QPushButton(u'Отмена')
		btnClose.clicked.connect(self.reject)
		mainLt.addWidget(QtGui.QLabel(u'Наименование проекта:'), 0, 0)
		mainLt.addWidget(self.edtName, 0, 1)
		mainLt.addWidget(QtGui.QLabel(u'Размещение:'), 1, 0)
		ltPath = QtGui.QHBoxLayout()
		ltPath.setContentsMargins(0, 0, 0, 0)
		ltPath.addWidget(self.edtPath)
		ltPath.addWidget(btnPath)
		mainLt.addLayout(ltPath, 1, 1)
		lt = QtGui.QHBoxLayout()
		lt.addStretch()
		lt.addWidget(self.btnAdd)
		lt.addWidget(btnClose)
		mainLt.addLayout(lt, 2, 0, 1, 2)
		self.setLayout(mainLt)

	def _addProject(self):
		"""Подключает новый проект по введенным данным"""
		projectManager.addProject(u'%s' % self.edtName.text(), u'%s' % self.edtPath.text())
		self.accept()

	def _updateAddEnabled(self, value=None):
		"""Обновляет доступность добавления проекта по наименованию и пути"""
		self.btnAdd.setEnabled(self.edtName.text() != '' and self.edtPath.text() != '')

        def a(self, a):
            self.pth = a

	def __updatePath(self):
            """Открывает диалог выбора директории и обновляет путь проекта"""
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
