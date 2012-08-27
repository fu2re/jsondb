# -*- coding: utf-8 -*-
import re
from PyQt4 import QtCore, QtGui, Qt
from main.window import uni
from data.projects_manager import projectManager
from main.base.contextMenu import QContextMenu
from main.dialogue.template_add_field import FieldAddDialog
from main.base.selectBox import QSelectBox
from table_item import QTableItem

class QComboTable(QSelectBox, QTableItem):
    def __init__(self, root, parent):
        self.root = root
        self.wrapper = parent
        QtGui.QComboBox.__init__(self, parent)
        self.currentIndexChanged.connect(self._memSave)

    def _memSave(self, index):
        if hasattr(self, '_activated'):
            self._val = '%s' % self.currentText()
            self.wrapper.wrapper._memSave(self)