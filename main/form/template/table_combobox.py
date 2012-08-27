# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from main.base.selectBox import QSelectBox

class QComboTable(QSelectBox):
    def __init__(self, root, parent):
        self.wrapper = parent
        QtGui.QComboBox.__init__(self, parent)
        self.currentIndexChanged.connect(self._mem_save)

    def _mem_save(self, index):
        if hasattr(self, '_activated'):
            if self._field in ('blank', 'dynamic', 'is_file', 'nocompress'):
                self._val = self.itemData(index).toPyObject()

            elif self._field == 'foreign_key':
                self._val = '%s' % self.currentText()

#            elif self._field == 'values':
#                self._val = '%s' % self.currentText()

            elif self._field == 'kind':
                self._val = '%s' % self.currentText()


            self.wrapper.wrapper._mem_save(self)