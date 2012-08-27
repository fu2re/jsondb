# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, Qt

class Tab(QtGui.QTabWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QTabWidget.__init__(self, *args, **kwargs)
        self.tabCloseRequested.connect(self._tabRemoved)
        self.currentChanged.connect(self._tabChanged)
        self.setMovable(True)
        self.setTabsClosable(True)
        self._tabs = {}

    def _addTab(self, obj, context, table_name):
        """
        Удобно добавляем новую вкладку,
        Открывает новую вкладку,
        или активирует соответствующую вкладку если она уже существует
        """
        if obj not in self._tabs:
#           context._fill(table.all())
            tab = self.addTab(context, table_name)
            self._tabs[obj] = self.widget(tab)
            self.setCurrentIndex(tab)
        else:
            tab = self._tabs[obj]
            self.setCurrentWidget(tab)

    # Манипуляции вкладками, для корректного открытия без повторов

    def _tabRemoved(self, index):
        indeces = dict([(v, k) for k, v in self._tabs.items()])
        del self._tabs[indeces[self.widget(index)]]
        self.removeTab(index)

    def _tabChanged(self, index):
        w = self.widget(index)
        if w: w._update()

    def _removeAll(self):
        while self.currentIndex() >= 0:
            self.removeTab(self.currentIndex())
        self._tabs = {}