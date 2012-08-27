# -*- coding: utf-8 -*-
import os
from PyQt4 import QtCore, QtGui
from filter import QFilter
from table import QTable
from main.base.QRemoteImage import QRemoteImage
from data.projects_manager import projectManager

class QBox(QtGui.QSplitter):
    def __init__(self, project_name, table_name, table, root):
        self.project_name = project_name
        self.table_name = table_name
        self.table = table
        self.root = root
        QtGui.QSplitter.__init__(self)

        self.grid = QtGui.QGridLayout()

        self.filter = QFilter(root, self)
        self.doctable = QTable(root, self)        
        self.grid.addWidget(self.filter, 0, 0)
        self.grid.addWidget(self.doctable, 1, 0)
        self.setLayout(self.grid)

        self.splitterMoved.connect(self._saveState)
        self.restoreState(
            self.root.window.settings.value("table/state").toByteArray()
        )

    def _saveState(self):
        """
        Сохраняем геометрию
        """
        self.root.window.settings.setValue(
            "table/state", self.saveState()
        )

    def _update(self, *args):
        """
        Обновляем таблицу если был изменен хотя бы один документ в ней
        """
        if self.root._dy_unchanged(self.table) or \
        not hasattr(self, 'firstshow'):
            self.filter._search()
            self.firstshow = True

    def _memSave(self, item):
        """
        Сохраняем изменения в память
        """
        if not hasattr(item, '_activated'):
            return

        self.root._changed(item._doc)
        self.root._dy_changed(item._doc.t)
        try:
            if not isinstance(item, QRemoteImage):
                item._val = '%s' % item.text()

            if item._val == '' and self.doctable._structure[item._addr].blank:
                item._doc.remove(item._addr)

            else:
                item._doc.set(
                    item._addr,
                    projectManager.converter[self.doctable._structure[item._addr].kind](item._val),
                    False
                )
                item._before = item._val

        except (UnicodeEncodeError, ValueError):
            self.root._message(
                u'Ошибка типа значения, пожалуйста укажите значение соответствующего типа'
            )
            item.setText(unicode(item._before))

        except:
            self.root._log()
            item.setText(unicode(item._before))