# -*- coding: utf-8 -*-
from main.base.contextMenu import QContextMenu
from PyQt4 import QtCore, QtGui

class QTableItem(object):
    def _buildMenu(self, parent):
        """
        Context menu of table item, shows with right click
        """
        self.menu = QContextMenu(parent)
        self.menu._actions((
            ('Удалить', self._remove),
        ))
        self._avaibility()
        return self.menu
    
    def _avaibility(self):
        if self._row._kind not in ('ddict', 'list'):
            self.menu.avaibility[self._remove].setEnabled(False)

    def _remove(self):
        self.wrapper.wrapper.doc.remove(
            self.root._getaddr(self._row._addr, self._field._fieldName),
            commit=False
        )
        self.root._changed(self.wrapper.wrapper.doc)
        self.root._dy_changed(self.wrapper.wrapper.doc.t)
        self.wrapper.wrapper.tree._update()
        self.wrapper.wrapper._editDocument(
            self.wrapper.wrapper.tree.currentItem()
        )

class QDocumentTableItem(QtGui.QTableWidgetItem, QTableItem):
    def __init__(self, root, parent, text):
        self.root = root
        self.wrapper = parent
        QtGui.QTableWidgetItem.__init__(self, text)

class QDocumentIdItem(QtGui.QTableWidgetItem):
    def __lt__(self, other):
        """
        Метод для корректной сортировке полей с числовыми значениями
        """    
        try:
            return float(self.data(0).toPyObject()) < float(other.data(0).toPyObject())
        except:
            return QtGui.QTableWidgetItem.__lt__(self, other)