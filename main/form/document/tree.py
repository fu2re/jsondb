# -*- coding: utf-8 -*-
import re
from PyQt4 import QtCore, QtGui, Qt
from main.window import uni
from data.projects_manager import projectManager
from main.base.contextMenu import QContextMenu
from main.dialogue.template_add_field import FieldAddDialog

from tree_item import QItem
from main.base.tree import QTree

class QDocTree(QTree):
    def __init__(self, root, parent):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.wrapper = parent
        self.root = root
        self._items = []
        self.setHeaderLabels([u'Дерево документа', u'Название поля'])
        self.setColumnCount(2)
#        self._update()

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            menu = item._build_menu(self)
            action = menu.exec_(self.mapToGlobal(event.pos()))
            menu._do(action)

    def _update(self):
        """
        Обновляем дерево если есть изменения
        """
        state = self.saveState()
        self.clear()        
        self._fill(self._add('root', self.wrapper.doc.get()), ('id',))
        self.restoreState(state)        

    def _fill(self, parent, exclude=()):
        """
        Заполняем дерево
        """
        parent._kind = self.wrapper.table.__kind__(parent._addr)
        parent._sf = [
            field for field, data in parent._structure.keys.items()
            if data['$format']['kind'] not in ('dict', 'list')
        ]
        parent._setIcon()

        if type(parent._data) is dict:
            parent_data = parent._data.items()
        else:
            parent_data = enumerate(parent._data)

        for field, data in parent_data:
            if field in exclude:
                continue

            if type(data) in (list, dict):
                item = self._add(field, data, parent)
                self._fill(item)

            elif field not in parent._sf:
                parent._sf.append(field)
                
        self.expandAll()
        self.resizeColumnToContents(0)
        self.collapseAll()
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def _add(self, field, data, parent=None):
        """
        Возвращает Эелемент дерева готовый к вставке
        В качестве называния использует имя поля
        или описание поля(закоментировано)
        """
        item = QItem(self.root, self, [str(field)])
        item._data = data
        item._field = str(field)
        
        if parent:
            item._addr = self.root._getaddr(parent._addr, field)
            fulltext = parent._structure.kind not in ('list', 'ddict')
            parent.addChild(item)
        else:
            item._addr = ''
            fulltext = True
            self.addTopLevelItem(item)

        self._items.append(item)
        item._structure = self.wrapper.table.__field__(item._addr)
        if item._structure.text and fulltext:
            item.setText(1, item._structure.text or '')
        item.setToolTip(0, u'Адрес: %s\nТип: %s' % (item._addr, item._structure.kind))
        return item


