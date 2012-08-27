# -*- coding: utf-8 -*-
import os
from PyQt4 import QtCore, QtGui
from main.window import uni
from main.base.contextMenu import QContextMenu
from main.dialogue.ensure import EnsureDialog

class QTableItem(QtGui.QTableWidgetItem, uni):
    def __init__(self, root, parent, text):
        self.root = root
        self.wrapper = parent
        QtGui.QTableWidgetItem.__init__(self, text)

    def _build_menu(self, parent):
        self.menu = QContextMenu(parent)
        self.menu._actions((
#            ('Добавить элемент', self._add),
            ('Удалить', self._remove),
        ))
        return self.menu

    def __lt__(self, other):
        """
        Метод для корректной сортировке полей с числовыми значениями
        """
        try:
            return float(self.data(0).toPyObject()) < float(other.data(0).toPyObject())
        except:
            return QtGui.QTableWidgetItem.__lt__(self, other)        

    def _add(self):
        """
        Добавляем документ в таблицу
        """
        dialog = EnsureDialog(
            self.root, self,
            u'''
            Добавить новый документ?
            ''',
            u'Новый документ'
        )
        if dialog.exec_() == QtGui.QDialog.Accepted:
            new = self.wrapper.wrapper.table.new(commit=False)
            self.root._changed(new)
            self.wrapper.wrapper.filter._clear()
            self.wrapper._fill(self.wrapper.wrapper.table.all(), new.id)

    def _remove(self):
        """
        Удаляем документ из таблицы
        """
        dialog = EnsureDialog(
            self.root, self,
            u'''
            Это действие безвозвратно удалит документ %s.
            Документ также будет удален с жесткого диска.
            Вы уверены?
            ''' % self._doc.id,
            u'Удалить документ'
        )
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.root._unchanged(self._doc)
            self._doc.delete()
            self.wrapper._fill(self.wrapper.wrapper.table.all())

            if self._doc in self.root.tab._tabs:
                self.root.tab.removeTab(
                    self.root.tab.indexOf(
                        self.root.tab._tabs[self._doc]
                    )
                )