# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtCore, QtGui
from data.projects_manager import projectManager
from main.base.hgthread import HgThread
from data.stdout import FakeStdout
import time
from __resizable__ import Resizable

class HgDialogue(QtGui.QDialog, Resizable):
    """
    Диалог для иппортиа csv
    """
    script = {
        'commit':(
            u'Зафиксировать',
            {'message':''},
            u'Фиксация и проталкивание в удаленный репозиторий'
        ),
        'update':(
            u'Обновить',
            {},
            u'Обновить базу из удаленного репозитория, уничтожит все изменения в базе'
        )
    }

    def __init__(self, root, parent=None,  action='commit'):
        self.root = root
        self.wrapper = parent
        self.stdout = FakeStdout()
        self.args = self.script[action]
        self._continue = True
        QtGui.QDialog.__init__(self, None)
        self._restoreGeom('dialog/mercurial/geometry', 400, 250)
        self.setWindowTitle(self.args[0])
        self.grid = QtGui.QGridLayout()
        self.action = action
        self.grid.addWidget(QtGui.QLabel(self.args[2]), 0, 0, 1, 2)
        if action == 'commit':
            self.message = QtGui.QLineEdit()
            self.message.textChanged.connect(self._txchanged)
            self.grid.addWidget(QtGui.QLabel(u'Текст фиксации'), 1, 0)
            self.grid.addWidget(self.message, 1, 1)

        self.output = QtGui.QPlainTextEdit()
        self.output.setReadOnly(True)

        self.grid.addWidget(self.output, 2, 0, 1, 2)
        self._setupBase()

    def _setupBase(self):
        self.btnAdd = QtGui.QPushButton(u'Ок')
        self.btnAdd.setEnabled(False)
        self.btnAdd.clicked.connect(self.accept)
        self.btnGo = QtGui.QPushButton(u'Выполнить')
        self.btnGo.clicked.connect(self._run)
        btnClose = QtGui.QPushButton(u'Отмена')
        btnClose.clicked.connect(self.reject)
        lt = QtGui.QHBoxLayout()
        lt.addStretch()
        lt.addWidget(self.btnAdd)
        lt.addWidget(self.btnGo)
        lt.addWidget(btnClose)

        self.grid.addLayout(lt, 3, 0, 1, 2)
        self.setLayout(self.grid)        


    def newline(self):
        nl = '%s' % self.stdout.read()        
        if nl:
            self.output.insertPlainText(nl)
            self.repaint()


    def _run(self):        
        thread = HgThread(self.wrapper, self, self.action, self.args[1])
        thread.start()
        while True:
            if not self._continue:                
                self.btnAdd.setEnabled(True)
                break
            else:
                self.newline()
                time.sleep(0.1)


    def _txchanged(self):
        self.args[1]['message'] = unicode('%s' % self.message.text())
        
        