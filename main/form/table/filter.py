# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from main.window import uni
#from main.base.QRemoteImage import QRemoteImage

class QFilter(QtGui.QWidget, uni):
    def __init__(self, root, wrapper):
        self.root = root
        self.wrapper = wrapper

        QtGui.QWidget.__init__(self)
        self.grid = QtGui.QFormLayout()
        self.setLayout(self.grid)

        showAll = QtGui.QPushButton(self._to_utf('Очистить фильтр'))
        addField = QtGui.QPushButton(self._to_utf('Добавить поле'))

        showAll.clicked.connect(self._all)
        addField.clicked.connect(self._add)
        
        self._items = []

        self.grid.addRow(addField)
        self._add_id()
        self.grid.addRow(showAll)
        self._add()
        
    def _clear(self):
        for item, value in self._items:            
            value.setText('')
            try:
                item.setCurrentIndex(0)
            except:
                pass

    def _all(self):
        self._clear()
        qs = self.wrapper.table.all()
        self._message(len(qs))
        self.wrapper.doctable._fill(qs)


    def _search(self):
        qs = self.wrapper.table.all()
        for item, value in self._items:
            if value.text():
                addr, value, kind = self._val(item, value)
                if addr =='id' or kind != 'str':
                    qs = qs.filter(addr, value)
                else:
                    qs = qs.filter('%s__icontains' % addr, value)

        self._message(len(qs))
        self.wrapper.doctable._fill(qs)

    def _message(self, count):
        self.root._message(u'%s documents founded' % count)

    def _val(self, item, value):
        val= '%s' % value.text().toUtf8()
        if isinstance(item, QtGui.QLabel):
            return 'id', int(val), None
        else:
            addr = u'%s' % item.currentText().toUtf8()

        kind = self.wrapper.table.__kind__(addr)
        if kind == 'float':
            return addr, float(val), kind
        elif kind == 'int':
            return addr, int(val), kind
        
        return addr, val, kind

    def _add(self):
        item = QtGui.QComboBox(self)
        item.addItems(self.wrapper.table.fields)
        item2 = QtGui.QLineEdit(u'%s' % '', item)
        item2.textChanged.connect(self._search)
        self._items.append((item, item2))

        row = self.grid.rowCount() - 1
        self.grid.insertRow(row, item, item2)

    def _add_id(self):
        item = QtGui.QLabel('id')
        item2 = QtGui.QLineEdit(u'%s' % '', item)
        item2.textChanged.connect(self._search)
        self._items.append((item, item2))
        self.grid.addRow(item, item2)

