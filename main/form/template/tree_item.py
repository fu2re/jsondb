# -*- coding: utf-8 -*-
from PyQt4 import QtGui
import os
from main.base.contextMenu import QContextMenu
from main.dialogue.template_add_field import FieldAddDialog
from main.dialogue.ensure import EnsureDialog


class QItem(QtGui.QTreeWidgetItem):
    """
    Элемент дерева шаблона - поле
    """
    def __init__(self, root, parent, name):
        self.wrapper = parent
        self.root = root
        QtGui.QTreeWidgetItem.__init__(self, name)

    def _build_menu(self, name):
        """
        Context menu of table item, shows with right click
        """
        self.menu = QContextMenu(name)
        self.menu._actions((
            ('Добавить элемент', self._addChild),
            ('Удалить', self._remove),
        ))
        self._avaibility()
        return self.menu

    def _avaibility(self):
        if self.text(0) == '$items' or not self.parent():
            self.menu.avaibility[self._remove].setEnabled(False)

        if not self.static:
            self.menu.avaibility[self._addChild].setEnabled(False)



    def _addChild(self):
#        item = self.wrapper.currentItem()

        dialog = FieldAddDialog(self.root, self)
        if dialog.exec_() == QtGui.QDialog.Accepted:
#            self.__updateProjectList()
#            print field._kwargs
            self.wrapper.wrapper.table.add(
                self._addr,
                dialog._name,
                dialog._kind,
                commit=False,
                **dialog._kwargs
            )
            self.wrapper._update()
            self.root._changed(self.wrapper.wrapper.table)
            self.root._dy_changed(self.wrapper.wrapper.table)
            for i in self.wrapper.wrapper.table.objects.values():
                self.root._changed(i)

    def _remove(self):
        item = self.wrapper.currentItem()
        dialog = EnsureDialog(
            self.root,
            text=u"""
            Это действие удалит поле в шаблоне, и всех документах таблицы. 
            Вы уверены?
            """
        )
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.wrapper.setCurrentItem(item.parent())
            self.wrapper.wrapper._editDocument(item.parent())

            self.wrapper.wrapper.table.remove(
                item._addr,
                commit=False
            )
            self.wrapper._update()
            self.root._changed(self.wrapper.wrapper.table)
            for i in self.wrapper.wrapper.table.objects.values():
                self.root._changed(i)
                
    def _setIcon(self):
        self.static = True if self._kind == 'dict' and not self._data['$format'].get('dynamic') \
            else False

        if self.static:
            ico = 'list.png'
        else:
            ico = 'dict.png'
        self.setIcon(0, QtGui.QIcon(os.path.join('ui', ico)))