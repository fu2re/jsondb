# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtGui

class Step(QtGui.QDialog):
    """
    Диалог выполнения пользовательского скрипта
    """
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.grid = QtGui.QGridLayout()
        self.mlm = QtGui.QHBoxLayout()
        self._clear()
        self.grid.addLayout(self.mlm, 0, 0)
        self.resize(400, 250)
        self._setupBase()
        
#        print self._progress, type(self._progress)
    def __block__(self):
        self.btnPrev.setEnabled(False)
        self.btnGo.setEnabled(False)

    def __finish__(self):
        self.btnAdd.setEnabled(True)
        self.btnClose.setEnabled(False)

    def _nxt(self):
        self._chg(lambda x: x + 1)

    def _prv(self):
        self._chg(lambda x: x - 1)

    def _chg(self, f):
        self.currentStep = self.steps[f(self.steps.index(self.currentStep))]
        self.btnGo.setEnabled(not self.currentStep == self.steps[-1])
        self.btnPrev.setEnabled(not self.currentStep == self.steps[0])
        self.currentStep()

    def _setupBase(self):
        self.btnAdd = QtGui.QPushButton(u'Ок')
        self.btnAdd.setEnabled(False)
        self.btnAdd.clicked.connect(self.accept)
        self.btnPrev = QtGui.QPushButton(u'Назад')
        self.btnPrev.clicked.connect(self._prv)
        self.btnPrev.setEnabled(False)
        self.btnGo = QtGui.QPushButton(u'Далее')
        self.btnGo.clicked.connect(self._nxt)
        self.btnClose = QtGui.QPushButton(u'Отмена')
        self.btnClose.clicked.connect(self.reject)
        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(self.btnPrev)
        lt.addWidget(self.btnGo)
        lt.addWidget(self.btnClose)

        self.grid.addLayout(lt, 3, 0, 1, 2)
        self.setLayout(self.grid)

    def _addLayout(self, text, widget):
        if isinstance(self.mlt, QtGui.QFormLayout):
            self.mlt.addRow(text, widget)
        else:
            self.mlt.addWidget(widget)

    def _clear(self, flat=False):
        if hasattr(self, 'mltw'):
            self.mltw.hide()
            self.mlm.removeItem(self.mlm.itemAt(0))

        self.mltw = QtGui.QWidget()
        self.mlt = QtGui.QVBoxLayout() if flat else QtGui.QFormLayout()
        self.mltw.setLayout(self.mlt)
        self.mlm.addWidget(self.mltw)

    def _show(self, text):
        if hasattr(self, 'mltw'):
            self.mltw.hide()
            self.mlm.removeItem(self.mlm.itemAt(0))

        self.mltw = QtGui.QPlainTextEdit(text)
        self.mltw.setReadOnly(True)
        self.mlm.addWidget(self.mltw)

