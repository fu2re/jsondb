# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from data.projects_manager import projectManager
from table_combobox import QComboTable

class QDocTable(QtGui.QTableWidget):
    """
    Таблица свойств поля в шаблоне
    Представлена в виде таблицы
    """
    def __init__(self, root, parent):
        self.root = root
        self.wrapper = parent
        QtGui.QTableWidget.__init__(self, parent)
        self.setColumnCount(2)
        self.verticalHeader().setVisible(False)
        
    def combobox(self, value=None):
        """
        Функция добавления выпадающего списка,
        Возвращает объект списка
        """
        cb = QComboTable(self.root, self)
        if not value is None:
            cb.standart(value)
        return cb

    def valueHuman(self, item, field, value, pos):
        """
        Заполняем ячейку таблицы,
        Выбираем подходящий виджет на основании типа ячейки,
        Выбираем установленные значения
        """
        if field in ('blank', 'dynamic', 'is_file', 'nocompress'):
            val = self.combobox(value)
            self.setCellWidget(pos, 1, val)

        elif field == 'foreign_key':
            val = self.combobox()
            tables = ['']
            tables.extend(self.wrapper.table.core.table.keys())
            val.addItems(tables)
            val.setCurrentIndex(tables.index(value))
            self.setCellWidget(pos, 1, val)

        elif field == 'kind':
            val = self.combobox()
            kinds = projectManager.pattern.keys()
            val.addItems(kinds)
            self.setCellWidget(pos, 1, val)

            val.setCurrentIndex(kinds.index(self.wrapper._kind(item._addr)))
            if item._field != '$items':
                val.setEnabled(False)

        else:
            oldValue = value
            if field == 'values':
                oldValue = ', '.join(['%s' % i for i in value])
            val = QtGui.QTableWidgetItem('%s' % oldValue)
            self.setItem(pos, 1, val)
            val._before = oldValue

        val._val = value
        val._row = item
        val._field = field
        item._activated = True
        val._activated = True


    def _fill(self, item):
        """
        Формируем таблицу,
        выбираем подходящий сценарий, основываясь на типе поля
        """
        self.clear()
        self.setRowCount(0)
        pattern = projectManager.pattern[self.wrapper._kind(item._addr)].items()

        for field, requred in pattern:
            if (field == 'blank' and not item._addr):
                continue

            value = self.wrapper.table.structure(item._addr)['$format'].get(field)
            if value is None:
                value = ''

            self.insertRow(self.rowCount())
            pos = self.rowCount() - 1

            label = QtGui.QTableWidgetItem(u'%s' % field)
            if requred:
                label.setFont(self.root.boldFont)

            label.setFlags(QtCore.Qt.ItemIsEditable)
            self.setItem(pos, 0, label)
            self.valueHuman(item, field, value, pos)
        self.setHorizontalHeaderLabels((u'Ключ', u'Значение'))

