# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from main.base.contextMenu import QContextMenu
from main.dialogue.document_add_field import FieldAddDialog
from main.dialogue.ensure import EnsureDialog
from main.dialogue.input import InputDialugue

class QItem(QtGui.QTreeWidgetItem):
    """
    Элемент дерева шаблона - поле
    """
    def __init__(self, root, parent, name):
        self.wrapper = parent
        self.root = root
        QtGui.QTreeWidgetItem.__init__(self, name)

    def _build_menu(self, parent):
        """
        Context menu of table item, shows with right click
        """
        self.menu = QContextMenu(parent)
        self.menu._actions((
            ('Добавить элемент', self._addChild),
            ('Переименовать', self._rename),
            ('Удалить', self._remove)
        ))
        self._avaibility()
        return self.menu

    def _avaibility(self):
        if not self.parent():
            self.menu.avaibility[self._remove].setEnabled(False)
            self.menu.avaibility[self._rename].setEnabled(False)

        else:
            if not (self.parent()._kind in ('ddict', 'list') or \
            self._structure.blank):
                self.menu.avaibility[self._remove].setEnabled(False)

            if self.parent()._kind != 'ddict':
                self.menu.avaibility[self._rename].setEnabled(False)


        if not (self._kind in ('ddict', 'list') or self._hiddenProp()):
            self.menu.avaibility[self._addChild].setEnabled(False)
                    
            
    def _hiddenProp(self):
        return set(self._structure.keys) - set(self._sf)\
        - set(self.wrapper.wrapper.doc.get(self._addr))

    def _remove(self):
        dialog = EnsureDialog(
            self.root, self, 
            u"Это действие удалит поле %s.\nВы уверены?" % self._addr,
            u'Удалить поле'
        )
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.wrapper.setCurrentItem(self.parent())
            self.wrapper.wrapper.doc.remove(self._addr, commit=False)
            self.wrapper._update()
            self.wrapper.wrapper._editDocument(self.wrapper.currentItem())            
            self.root._changed(self.wrapper.wrapper.doc)
            self.root._dy_changed(self.wrapper.wrapper.table)

    def _addChild(self):
        dialog = FieldAddDialog(self.root, self)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            if self._kind == 'dict':
                self.wrapper.wrapper.doc.set(
                    self.root._getaddr(self._addr, dialog._field),
                    commit=False
                )
            else:
                try:
                    self.wrapper.wrapper.doc.add(
                        self._addr,
                        key=dialog._field,
                        commit=False
                    )
                except:
                    self.root._log()
            self.root._dy_changed(self.wrapper.wrapper.table)
            self.root._changed(self.wrapper.wrapper.doc)
            self.wrapper.wrapper._update()
            

    def _rename(self):
        dialogue = InputDialugue(
            self.root, self, u'Новое имя', self.text(0)
        )
        if dialogue.exec_() == QtGui.QDialog.Accepted:
            if not dialogue._val:
                return
            self.wrapper.wrapper.doc.__move__(
                self._addr,
                self.root._getaddr(
                    self.parent()._addr, dialogue._val
                ), False)
            self.wrapper._update()
            self.root._changed(self.wrapper.wrapper.doc)

    def _setIcon(self):
        if self._kind == 'dict':
            ico = 'dict.png'
        else:
            ico = 'list.png'
        self.setIcon(0, QtGui.QIcon(os.path.join('ui', ico)))

    def __lt__(self, other):
        """
        Метод для корректной сортировке полей с числовыми значениями
        """
        try:
            return float('%s' % self.text(0)) < float('%s' % other.text(0))
        except:
            return QtGui.QTreeWidgetItem.__lt__(self, other)