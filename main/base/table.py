# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from table_combobox import QComboTable
from table_item import QDocumentTableItem
from main.window import uni

class QDocTable(QtGui.QTableWidget):
    """
    Таблица свойств поля в шаблоне
    Представлена в виде таблицы
    """
    def __init__(self, root, parent):
        self.root = root
        self.wrapper = parent
        QtGui.QTableWidget.__init__(self, parent)

    def _fill(self, item=None):
        item = item or self.wrapper.tree.currentItem()
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(2)

#        id = u'%s' % item.text(0)

        for field in item._sf:
            self.insertRow(self.rowCount())
            value, labelName = self._getValue(item, field)
            pos = self.rowCount() - 1
            label = QtGui.QTableWidgetItem(u'%s' % labelName)
            label._fieldText = labelName
            label._fieldName = field
            label._row = item

            if not item._kind == 'ddict':
                label.setFlags(QtCore.Qt.ItemIsEditable)

            if item._kind == 'dict':
                if not item._structure.pattern[field]['$format'].get('blank'):
                    label.setFont(self.root.boldFont)

            self.setItem(pos, 0, label)
            self.valueHuman(item, label, value, pos)
        self.resizeColumnsToContents()

    def _getValue(self, item, field):
        addr = self.root._getaddr(item._addr, field)
        value = self.wrapper.doc.get(addr)
        if value is None:
            value = ''

        labelName = field
        if self.wrapper.table.__field__(item._addr).kind not in ('ddict', 'list'):
            labelName = self.wrapper.table.__field__(addr).text or field

        return value, labelName


    def valueHuman(self, item, label, value, pos):
        """
        Заполняем ячейку таблицы,
        Выбираем подходящий виджет на основании типа ячейки,
        Выбираем установленные значения
        """
        structure = self.wrapper.table.__field__(
            self.root._getaddr(item._addr, label._fieldName)
        )
        choices = structure.values
        if choices:
            val = QComboTable(self.root, self)
            if structure.blank:
                choices.insert(0, '')
            val.addItems([str(i) for i in choices])
            val.setCurrentIndex(choices.index(value))
            self.setCellWidget(pos, 1, val)

        else:
            val = QDocumentTableItem(self.root, self, '%s' % value)
            val._before = value
            self.setItem(pos, 1, val)

        val._val = value
        val._row = item
        val._field = label
        item._activated = True
        val._activated = True
#
#
#    def combine(self, item):
#        """
#        Формируем таблицу,
#        выбираем подходящий сценарий, основываясь на типе поля
#        """
#        pattern = projectManager.pattern[self.wrapper._kind(item._addr)].items()
#
#        for field, requred in pattern:
#            if (field == 'blank' and not item._addr):
#                continue
#
#            value = self.wrapper.table.structure(item._addr)['$format'].get(field)
#            if value is None:
#                value = ''
#
#            self.insertRow(self.rowCount())
#            pos = self.rowCount() - 1
#
#            label = QtGui.QTableWidgetItem(u'%s' % field)
#            if requred:
#                label.setFont(self.root.boldFont)
#
#            label.setFlags(QtCore.Qt.ItemIsEditable)
#            self.setItem(pos, 0, label)
#            self.valueHuman(item, field, value, pos)
#
    def contextMenuEvent(self, event):
        """
        Context menu of project item, shows with right click
        """
        item = self.itemAt(event.pos())
        if item:
            menu = item._buildMenu(self)
            action = menu.exec_(self.mapToGlobal(event.pos()))
            menu._do(action)


