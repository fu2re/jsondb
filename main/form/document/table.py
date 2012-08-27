# -*- coding: utf-8 -*-
import Queue
import copy
from PyQt4 import QtCore, QtGui
from table_combobox import QComboTable
from table_item import QDocumentTableItem, QDocumentIdItem
from main.base.QRemoteImage import QRemoteImage
from main.base.webthread import WebThread
from main.window import uni

class QDocTable(QtGui.QTableWidget, uni):
    """
    Таблица свойств поля в шаблоне
    Представлена в виде таблицы
    """
    def __init__(self, root, parent):
        self.root = root
        self.wrapper = parent
        self.queue = Queue.Queue()
        self.thread = WebThread(root, self)        
        self.connect(
            self.thread,
            QtCore.SIGNAL('taskDone(PyQt_PyObject, bool, QString, bool)'),
            self._taskDone, QtCore.Qt.QueuedConnection
        )
        self.connect(self.thread, QtCore.SIGNAL('finished()'), self._taskFinished)       

        QtGui.QTableWidget.__init__(self, parent)        
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setColumnCount(2)

        self.verticalHeader().setVisible(False)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            menu = item._buildMenu(self)
            action = menu.exec_(self.mapToGlobal(event.pos()))
            menu._do(action)

    def _taskDone(self, item, ispix, val, remote):
        """
        Обновляет и отображает картинку,
        при необходимости делает ресaйз row
        """
        item.toPyObject()._get_finished(ispix, '%s' % val, remote)

    def _taskFinished(self):
        """
        Делаем ресайз всех rows когда все ячейки будут обработаны
        """
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def _fill(self, item=None):
        """
        Заполняем таблицу
        """
        item = item or self.wrapper.tree.currentItem()
        self.clear()
        self.setRowCount(0)
        for field in item._sf:
            self.insertRow(self.rowCount())
            value, labelName = self._getValue(item, field)
            pos = self.rowCount() - 1
            label = QDocumentIdItem(u'%s' % labelName)
            label._fieldText = labelName
            label._fieldName = field
            label._row = item
            label._target = self.root._getaddr(item._addr, field)
            label.setToolTip(label._target)
            
            if not item._kind == 'ddict':
                label.setFlags(QtCore.Qt.ItemIsEditable)

            if item._kind == 'dict':
                if not item._structure.pattern[field]['$format'].get('blank'):
                    label.setFont(self.root.boldFont)

            self.setItem(pos, 0, label)
            label._activated = True
            self.valueHuman(item, label, value, pos)
        self.thread.start()
        self.setHorizontalHeaderLabels((u'Ключ', u'Значение'))
        self.sortItems(0)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def _getValue(self, item, field):
        """
        Возвращает имя поля или его описание(если есть) и оригинальное значение
        """
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
#        target = self.root._getaddr(item._addr, label._fieldName)
        structure = self.wrapper.table.__field__(label._target)
        choices = copy.copy(structure.values)
        if choices:
            val = QComboTable(self.root, self)
            if structure.blank:
                choices.insert(0, '')
            val.addItems([str(i) for i in choices])
            val.setCurrentIndex(choices.index(value))
            self.setCellWidget(pos, 1, val)

        else:
            if structure.is_file:
                val = QRemoteImage(self.root, self, '%s' % value)
                self.setCellWidget(pos, 1, val)
            else:
                val = QDocumentTableItem(self.root, self, '%s' % value)
                val._before = value
                self.setItem(pos, 1, val)

        if structure.foreign:
            val.setToolTip(self.wrapper.doc.get_related(label._target).helptext)

        val._val = value
        val._row = item
        val._field = label
        item._activated = True
        val._activated = True

    def _memSave(self, item):
        self.wrapper._memSave(item)


