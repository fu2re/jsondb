# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from tree_item import QItem
from main.base.tree import QTree

class QDocTree(QTree):
    """

    """
    def __init__(self, root, parent):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.wrapper = parent
        self.root = root
        self._items = []
        self._update()
        self.setHeaderLabel(u'Дерево шаблона')
        self.setCurrentItem(self.topLevelItem(0))

    def _update(self):
        state = self.saveState()
        self.clear()
        self._fill(self._add('root', self.wrapper.table.structure()))
        self.restoreState(state)

    def _fill(self, parent):
#        print parent._addr
        parent._kind = parent._data['$format']['kind']
        parent._setIcon()

        for field, data in parent._data.items():
            if field != '$format':
                item = self._add(field, data, parent)
                self._fill(item)

    def _add(self, field, data, parent=None):
        item = QItem(self.root, self, [str(field)])
        item._data = data
        item._field = str(field)
        if parent:
            item._addr = '.'.join(
                (parent._addr, str(field))
            ) if parent._addr else field
            parent.addChild(item)
        else:
            item._addr = ''
            self.addTopLevelItem(item)
        self._items.append(item)

        return item

    def contextMenuEvent(self, event):
        """
        Context menu of project item, shows with right click
        """
        item = self.itemAt(event.pos())
        if item:
            menu = item._build_menu(self)
            action = menu.exec_(self.mapToGlobal(event.pos()))
            menu._do(action)
