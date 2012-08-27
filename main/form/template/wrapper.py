# -*- coding: utf-8 -*-
import sys
import traceback
from PyQt4 import QtGui
from main.window import uni
from data.projects_manager import projectManager

from table import QDocTable
from tree import QDocTree
from tree_item import QItem
from table_combobox import QComboTable


class QTemplate(QtGui.QSplitter, uni):
    def __init__(self, project_name, table_name, table, root):
        self.project_name = project_name
        self.table_name = table_name
        self.table = table
        self.root = root

        QtGui.QSplitter.__init__(self)
        self.grid = QtGui.QGridLayout()        

        self.tree = QDocTree(root, self)
        self.doctable = QDocTable(root, self)
        self._editDocument()
        
        self.grid.addWidget(self.tree, 0, 0)
        self.grid.addWidget(self.doctable, 0, 1)
        
        
        self.setLayout(self.grid)

        self.tree.itemClicked.connect(self._editDocument)
#        self.doctable.itemDoubleClicked.connect(self._activate)
        self.doctable.itemChanged.connect(self._mem_save)

#        self.saveAction = QtGui.QAction("&Save", self);
#        self.saveAction.connect(self.save)
        self.splitterMoved.connect(self._saveState)
        self.restoreState(
            self.root.window.settings.value("pattern/state").toByteArray()
        )

    def _saveState(self):
        self.root.window.settings.setValue(
            "pattern/state", self.saveState()
        )

    def _update(self, *args):
        pass

    def _editDocument(self, item=None):
        item = item or self.tree.currentItem()
        self.doctable._fill(item)


    def _getaddr(self, prefix, postfix):
        if prefix:
            return '.'.join((str(prefix), str(postfix)))
        else:
            return postfix

    def _mem_save(self, item):
        if hasattr(item, '_activated'):
            self.root._changed(self.table)
            self.root._dy_changed(self.table)
            if not isinstance(item, QComboTable):
                item._val = '%s' % item.text()

            try:
                kw = {item._field: self._get_val(item)}
                if item._field == 'kind':
                    if item._val == 'dynamic dict':
                        kw = {'kind':'dict', 'dynamic':1}
                    if kw['kind'] in self.table.core.defaults:
                        kw['default'] = self.table.core.defaults[kw['kind']]
#                print item._row._addr, kw
                self.table.change(
                    item._row._addr,
                    False,
                    **kw
                )
                if item._field == 'kind':
                    item._row._kind = item._val
                self.root.window.statusbar.showMessage('ready')
                
            except:
                self.root._log()

            self._editDocument(item._row)
            self.tree._update()



    def _get_val(self, item):
        if not projectManager.pattern[self._kind(item._row._addr)][item._field] and \
            item._val == '':
                return None

        if item._field in ('min','max'):
            return float(item._val) if item._row._kind == 'float' else int(item._val)

        elif item._field == 'default':
            return self._convert(item, item._val)

        elif item._field == 'values':
            return [self._convert(item, i.strip()) for i in item._val.split(',')]

        else:
            return item._val

    def _convert(self, item, value):
        return projectManager.converter[item._row._kind](value)

    def save(self):
        if self.table in self.root.changed:
            self.root._unchanged(self.table)
            self.table.save()

    def _kind(self, addr):
        '''
        Возвращает внутренний тип поля, на основании внутреннего поля таблицы(в движке)
        Разница в том что в движке динамические словари именуются ddict
        В JsonDB Explorer они именуются dynamic dict
        '''
        ikind = self.table.__kind__(addr)
        if ikind == 'ddict':
            ikind = 'dynamic dict'
        return ikind