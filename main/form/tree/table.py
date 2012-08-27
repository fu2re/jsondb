# -*- coding: utf-8 -*-
import os
from PyQt4 import QtCore, QtGui, Qt
from main.dialogue.table_property import QTableProperty
from main.base.contextMenu import QContextMenu
from main.form.template.wrapper import QTemplate
from main.dialogue.ensure import EnsureDialog
from main.dialogue.export import ExportDialog
from main.dialogue.importCsv import ImportDialog

class QProjectTableItem(QtGui.QTreeWidgetItem,):
    """
    Второй уровень левого меню
    """
    def __init__(self, root, parent, name):
        QtGui.QTreeWidgetItem.__init__(self, name)
        self.root = root
        self.wrapper = parent
        self.setIcon(0, QtGui.QIcon(os.path.join('ui', 'project.png')))

    def _build_menu(self, parent):
        """
        Context menu of table item, shows with right click
        """
        self.menu = QContextMenu(parent)
        self.menu._actions((
            ('Добавить документ', self._addDocument),
            ('Импорт из csv', self._importTable),
            ('Экспорт в csv', self._exportTable),
            ('Удалить', self._delete),
            ('Свойства', self._property),
            ('Шаблон', self._openTemplate),
        ))
        return self.menu

    def _property(self):
        """
        Диалог свойств таблицы
        """
        project_name = self.parent()._project.name
        table_name = self.text(0)
#        table = projectManager.getProjectByName(u'%s' % project_name).data.table.get(u'%s' % table_name)
        property = QTableProperty(project_name, table_name, self._table, self.root)
        property.exec_()

    def _delete(self):
        """
        Удаляем таблицу
        """        
        name = '%s' % self.text(0)
        dialogue = EnsureDialog(
            self,
            text=u"""
            Это действие удалит таблицу %s, и все ее документы
            Вы уверены?
            """ % name
        )
        if dialogue.exec_() == QtGui.QDialog.Accepted:
            self.parent()._project.data.table[name].delete()
            self.parent().removeChild(self)
            del self

    def _openTemplate(self, item=None):
        """
        открываем шаблон таблицы,
        если такая вкладка уже есть, то делаем ее активной
        """
        project_name = self.parent().text(0)
        table_name = self.text(0)
        self.root.tab._addTab(
            '%s_t' % self._table,
            QTemplate(project_name, table_name, self._table, self.root),
            '%s template' % table_name
        )

    #  Документы
    
    def _addDocument(self):
        """
        Создавем новый документ в таблице
        """
        new = self._table.new(commit=False)
        self.root._changed(new)
        self.root._openDocument(
            new.id,
            self._table,
            self._project.name
        )
        self.root._dy_changed(self._table)

    # CSV

    def _exportTable(self, item=None):
        """
        ЭКспортируем данные из тпблицы в csv файл
        """
        dialogue = ExportDialog(self.root, self)
        if dialogue.exec_() == QtGui.QDialog.Accepted:
            try:
                self.root._message(u'Wait')
                path = '%s.csv' % os.path.join(
                    u'%s' % dialogue.edtPath.text(),
                    '%s' % dialogue.edtName.text()
                )
                self._table.dumps(
                    path,
                    dialogue._fields
                )
                self.root._message(u'%s успешно создан' % path)
            except:
                self.root._log()

    def _importTable(self, item=None):
        """
        Импорт данных из csv файла в таблицу
        """
        dialogue = ImportDialog(self.root, self)
        if dialogue.exec_() == QtGui.QDialog.Accepted:
#                print dialogue._pth, dialogue.sync.checkState()
            try:
                self.root._message(u'Wait')
                self._table.loads(dialogue._pth, dialogue.sync.checkState())
                self.root._message(u'%s успешно загружен' % dialogue._pth)
            except:
                self.root._log()