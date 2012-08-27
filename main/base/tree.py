# -*- coding: utf-8 -*-
from PyQt4 import QtGui

class QTree(QtGui.QTreeWidget):
    def saveState(self):
        state = dict([
            (i._addr, (i.isExpanded(), i.isSelected()))
            for i in self._items
        ])
        self._items = []
        return state

    def restoreState(self, state):
        for i in self._items:
            if i._addr in state:
                i.setExpanded(state[i._addr][0])
                if state[i._addr][1]:
                    self.setCurrentItem(i)