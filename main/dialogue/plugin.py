# coding: utf-8
"""Модуль добавления проекта"""

from PyQt4 import QtCore, QtGui
import os
import sys
import re
import traceback
from __step__ import Step
from __resizable__ import Resizable

class Thread(QtCore.QThread):
    def __init__(self, root, parent):
        self.root = root
        self.wrapper = parent
        QtCore.QThread.__init__(self)

    def progressed(self, val):
        self.emit(QtCore.SIGNAL("progressed(float)"), val)

    def out(self, val):
        self.emit(QtCore.SIGNAL("print(QString)"), val)

    def run(self):
        self.wrapper.script.init(
            self, self.wrapper.project,
            dict([(i._name, u'%s' % i.text()) for i in self.wrapper.params])
        )
        try:
            self.wrapper.script.exec_()
        except:
            self.emit(QtCore.SIGNAL("print(QString)"), traceback.format_exc())

        self.emit(QtCore.SIGNAL("finished()"))

class CB(QtGui.QComboBox):
    def __init__(self, wrapper, elements):
        self.wrapper = wrapper
        self.elements = elements
        QtGui.QComboBox.__init__(self)
        self.addItems(self.elements)

class PluginDialog(Step, Resizable):
    """
    Диалог выполнения пользовательского скрипта
    """
    def __init__(self, root, project):
        self.currentStep = self.__discover
        self.steps = (
            self.__discover,
            self.__params,
            self.__progress
        )
        self.root = root
        self.scriptName = None
        self.project = project.data
        self.thread = Thread(self.root, self)
        self.connect(self.thread, QtCore.SIGNAL('progressed(float)'), self.__progressed)
        self.connect(self.thread, QtCore.SIGNAL('finished()'), self.__finish)
        self.connect(self.thread, QtCore.SIGNAL('print(QString)'), self.__newline)
        
        self._progress = 0
        self.path = os.path.join(self.project.path, 'scripts')
        Step.__init__(self, self.root.window)
        self._restoreGeom('dialog/plugin/geometry', 800, 300)
        self.setWindowTitle(u'Выполнить скрипт')

        self.cbd = QtGui.QPlainTextEdit()
        self.cbd.setReadOnly(True)
        self.cb = CB(self, [
            k for k in os.listdir(self.path)
            if re.search('.py$', k) and k != '__base__.py'
        ])
        self.connect(
            self.cb, QtCore.SIGNAL('currentIndexChanged(int)'),
            self.__getDiscription
        )
        self.__getDiscription()
        self.output = QtGui.QPlainTextEdit()
        self.output.setReadOnly(True)

        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.currentStep()

    def __newline(self, line):
        self.output.insertPlainText(u'%s\r' % line)
        self.repaint()
        
    def __discover(self):
        self._clear()
        self._addLayout(u'Скрипт', self.cb)
        self._addLayout(u'Скрипт', self.cbd)

    def __getDiscription(self):
        scriptName = '%s' % self.cb.currentText()
        scriptName = '.'.join(scriptName.split(".")[:-1])
        sys.path.append(self.path)
        self.cbd.clear()
        try:
            exec "from %s import description" % scriptName
            self.cbd.insertPlainText(description.strip("\n"))
        except:
            self.cbd.insertPlainText(u"Нет описания")
        self.repaint()
        sys.path.remove(self.path)
        
    def __params(self):
        scriptName = '%s' % self.cb.currentText()
        scriptName = '.'.join(scriptName.split(".")[:-1])
        if self.scriptName != scriptName:
            self.scriptName = scriptName
            sys.path.append(self.path)
            try:
                exec "from %s import Plugin" % scriptName
                self.script = Plugin()
                self.params = []
                for i in self.script.params:
                    w = QtGui.QLineEdit()
                    w._name = i
                    self.params.append(w)
            except:
                self.root._log(
                    str(sys.exc_info()[1]).decode('utf-8'),
                    traceback.format_exc()
                )
                self._prv()
            sys.path.remove(self.path)
        self._clear()
        for w in self.params:
            self._addLayout(u'%s' % w._name, w)

    def __progressed(self, val):
        self.progressBar.setValue(val*100)
        self.progressBar.repaint()

    def __progress(self):
        self._clear(True)
        self._addLayout(u'', self.progressBar)
        self._addLayout(u'', self.output)
        self.__block__()        
        self.thread.start()

    def __finish(self):
        self.progressBar.setValue(100)
        self.__finish__()
        self.btnPrev.setEnabled(True)
        self.root.changed.extend(self.project.core.changed)



