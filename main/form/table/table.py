# -*- coding: utf-8 -*-
import Queue
from PyQt4 import QtCore, QtGui
from main.window import uni
from table_item import QTableItem
from main.base.QRemoteImage import QRemoteImage
from main.base.webthread import WebThread

class QTable(QtGui.QTableWidget, uni):
    def __init__(self, root, wrapper):
        self.root = root
        self.wrapper = wrapper
        self.queue = Queue.Queue()
        self.thread = WebThread(root, self)
        self.connect(self.thread, QtCore.SIGNAL('finished()'), self._taskFinished)
        self.connect(
            self.thread,
            QtCore.SIGNAL('taskDone(PyQt_PyObject, bool, QString, bool)'),
            self._taskDone, QtCore.Qt.QueuedConnection
        )
        
        
        QtGui.QTableWidget.__init__(self)
        self.setSortingEnabled(True)
#        self.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.itemDoubleClicked.connect(self._editDocument)
        self.itemChanged.connect(self._memSave)
        fields = self.settings.value(
            "project/%s/%s/visible" % (self.wrapper.project_name, self.wrapper.table_name),
            ()
#            self.wrapper.table.simple_fields()
        ).toPyObject()

        self._fields = ['id']
        self._fields.extend(fields or [])
        self._labels = self._getLabels(fields)
        self._prepare()
#        self._fill(self.wrapper.table.all())
        
    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        menu = item._build_menu(self)
#        menu = self.selectedItems()[0]._build_menu(self)
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

    def _getLabels(self, fields):
        """
        Получаем лейблы для шапки таблицы
        """
        labels = ['id']
        for i in fields:
            addr = '%s' % i
            if addr and \
            self.wrapper.table.__field__('.'.join(addr.split('.')[:-1])).kind not in ('list', 'ddict'):
                labels.append(self.wrapper.table.__field__('%s' % i).text or i)
            else:
                labels.append(i)
        return labels

    def _editDocument(self, item=None):
        """
        Открываем документ по нажатию на колонку id
        """
        if hasattr(item, '_id'):
            self.root._openDocument(
                item._id,
                self.wrapper.table,
                self.wrapper.project_name
            )


    def _fill(self, data, current=None):
        """
        Заполяет таблицу данными lstData
        """
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(len(self._labels))
        self.setHorizontalHeaderLabels(self._labels)

        for doc in data:
            self.insertRow(self.rowCount())
            for k, field in enumerate(self._fields):                
                self.valueHuman(doc, field, self.rowCount() - 1, k)

        if self.rowCount() > 0:
            self.setCurrentCell(0, 0)
            
        self.thread.start()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


    def _prepare(self):
        """
        для ускорения работы
        получам структуры для всех доступных таргетов
        """
        self._structure = {}
        for i in self._fields:
            if i == 'id': continue
            self._structure['%s' % i] = self.wrapper.table.__field__('%s' % i)


    def valueHuman(self, doc, field, xpos, ypos):
        """
        Заполняем ячейку таблицы,
        Выбираем подходящий виджет на основании типа ячейки,
        Выбираем установленные значения

        Возможна поддержка ComboBox полей
        (закоментировано по причине медленной работы)
        """
        if field == 'id':
            val = QTableItem(self.root, self, u'%s' % doc.id)
            val._id = doc.id
            val.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.setItem(xpos, ypos, val)
            
        else:
            value = doc.get('%s' % field)
            if value is None:
                value = u''

    #        if field in self._choices:
    #            val = QComboTable(self.root, self)
    #            val.addItems(self._choices[field])
    #            try:
    #                val.setCurrentIndex(self._choices[field].index(value))
    #            except:
    #                pass
    #            self.setCellWidget(xpos, ypos, val)

            if self._structure['%s' % field].is_file:
                val = QRemoteImage(self.root, self, '%s' % value)
                self.setCellWidget(xpos, ypos, val)
            else:
                val = QTableItem(self.root, self, u'%s' % value)
                val._before = value
                self.setItem(xpos, ypos, val)

        val._doc = doc
        val._addr = '%s' % field
        val.setToolTip(field)
        val._activated = True

    def _memSave(self, item):
        """
        Сохраняем изменения в память
        """
        self.wrapper._memSave(item)