# coding: utf-8
"""Модуль отображения списка файлов для некоторой таблицы проекта"""

import os
from PyQt4 import QtCore, QtGui
from file_add_dialog import FileAddDialog


def getStyledLabel(text):
	"""Возвращает стилизованный label с текстом text"""
	lbl = QtGui.QLabel(text)
	lbl.setMinimumWidth(80)
	lbl.setFrameStyle(QtGui.QFrame.StyledPanel)
	lbl.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
	lbl.setAlignment(QtCore.Qt.AlignCenter)
	return lbl


class _ToolTip(QtGui.QDialog):
	def __init__(self, parent=None):
		super(_ToolTip, self).__init__(parent)
		self.setWindowFlags(QtCore.Qt.ToolTip)
		self.setWindowModality(False)
		lt = QtGui.QHBoxLayout()
		lt.setContentsMargins(0, 0, 0, 0)
		self.lbl = QtGui.QLabel('')
		self.lbl.setFrameShape(QtGui.QFrame.StyledPanel)
		lt.addWidget(self.lbl)
		self.setLayout(lt)

	def setToolTipPicture(self, fileName):
		"""Устанавливает картинку из адреса fileName"""
		self.lbl.setPixmap(QtGui.QPixmap(fileName))


class _ListWidget(QtGui.QListWidget):
	def __init__(self, parent=None):
		super(_ListWidget, self).__init__(parent)
		self.setMouseTracking(True)
		self.setAlternatingRowColors(True)
		self.toolTipWgt = _ToolTip()
		self.itemEntered.connect(self._runToolTip)

	def _runToolTip(self, item):
		self.toolTipWgt.close()
		filePath = item.data(QtCore.Qt.UserRole).toString()
		if filePath:
			pos = self.mapFromGlobal(self.cursor().pos())
			height = item.sizeHint().height() / 2 + pos.y()
			self.toolTipWgt.setToolTipPicture(filePath)
			self.toolTipWgt.move(self.mapToGlobal(QtCore.QPoint(5, height)))
			self.toolTipWgt.show()

	def mouseMoveEvent(self, event):
		if self.count() > 0:
			c = self.count() * self.item(0).sizeHint().height()
		else:
			c = 0
		scroll = self.verticalScrollBar()
		if event.pos().y() > c or (scroll.isVisible() \
				and event.pos().x() > self.width() - scroll.width() - 8):
			self.toolTipWgt.close()
		super(_ListWidget, self).mouseMoveEvent(event)

	def leaveEvent(self, event):
		self.toolTipWgt.close()


class FilesVewDialog(QtGui.QDialog):
	"""Диалог со списком фалов таблицы table проекта project"""

	def __init__(self, table, project, parent=None):
		super(FilesVewDialog, self).__init__(parent)
		self.table = table
		self.project = project
		self.setWindowTitle(u'Файлы')
		mainLt = QtGui.QGridLayout()
		mainLt.addWidget(QtGui.QLabel(u'Проект:'), 0, 0)
		mainLt.addWidget(QtGui.QLabel(u'Таблица:'), 1, 0)
		mainLt.addWidget(getStyledLabel(project.name), 0, 1)
		mainLt.addWidget(QtGui.QSplitter(), 0, 2)
		mainLt.addWidget(getStyledLabel(table), 1, 1)
		mainLt.addWidget(QtGui.QSplitter(), 1, 2)
		gbxFiles = QtGui.QGroupBox(u'Файлы')
		gbxLt = QtGui.QGridLayout()
		#self.lstFiles = QtGui.QListWidget()
		self.lstFiles = _ListWidget()
		self.btnAdd = QtGui.QPushButton(u'Добавить')
		self.btnAdd.clicked.connect(self._addFile)
		self.btnDelete = QtGui.QPushButton(u'Удалить')
		self.btnDelete.clicked.connect(self._deleteFile)
		gbxLt.addWidget(self.lstFiles, 0, 0, 3, 1)
		gbxLt.addWidget(self.btnAdd, 0, 1)
		gbxLt.addWidget(self.btnDelete, 1, 1)
		gbxFiles.setLayout(gbxLt)
		mainLt.addWidget(gbxFiles, 2, 0, 1, 3)
		btnClose = QtGui.QPushButton(u'Закрыть')
		btnClose.clicked.connect(self.close)
		ltBottom = QtGui.QHBoxLayout()
		ltBottom.setContentsMargins(0, 0, 0, 0)
		ltBottom.addStretch()
		ltBottom.addWidget(btnClose)
		mainLt.addLayout(ltBottom, 3, 0, 1, 3)
		self.setLayout(mainLt)
		self.resize(800, 600)

		self.__updateFilesList()

	def _addFile(self):
		"""Открывает диалог добавления файла в таблицу проекта"""
		dlg = FileAddDialog(self.table, self.project)
		if dlg.exec_() == QtGui.QDialog.Accepted:
			self.__updateFilesList()

	def _deleteFile(self):
		"""Удаляет выбранный файл"""
		file = u'%s' % self.lstFiles.currentItem().text()
		if QtGui.QMessageBox.question(self, u'Удаление файла',
			u'Удалить файл %s?' % file, u'ОК', u'Отмена') == QtGui.QMessageBox.NoButton:
			filePath = os.path.join(self.project.path, 'files', self.table, file)
			os.remove(filePath)
			self.__updateFilesList()

	def __updateFilesList(self):
		"""Обновляет данные о файлах таблицы и перестраивает их отображение"""
		self.lstFiles.clear()
		path = os.path.join(self.project.path, 'files', self.table)
		if os.path.isdir(path):
			for file in os.listdir(path):
				filePath = os.path.join(path, file)
				if os.path.isfile(filePath):
					item = QtGui.QListWidgetItem(file)
					item.setSizeHint(QtCore.QSize(90, 30))
					if file.lower().split('.')[-1] in ['png', 'jpeg', 'bmp']:
						item.setData(QtCore.Qt.UserRole, QtCore.QVariant(filePath))
					self.lstFiles.addItem(item)
		if self.lstFiles.count() > 0:
			self.lstFiles.setCurrentRow(0)
		self.__updateActionEnabled()

	def __updateActionEnabled(self):
		"""Обновляет доступность кнопок управления по выбору файла"""
		enabled = self.lstFiles.currentRow() >= 0
		self.btnDelete.setEnabled(enabled)
