# -*- coding: utf-8 -*-
import re
import os
from PyQt4 import QtCore, QtGui, Qt
from data.projects_manager import projectManager
from main.dialogue.project_property import ProjectProperty
from main.base.contextMenu import QContextMenu
from main.dialogue.input import InputDialugue
from main.dialogue.ensure import EnsureDialog
from main.dialogue.plugin import PluginDialog
from main.dialogue.amf import AMFDialog
from main.base.QWebWidget import WebView
from main.dialogue.hg import HgDialogue
from main.dialogue.table_new import TableNewDialugue
from main.dialogue.ensure import EnsureDialog
from main.form.tree.table import QProjectTableItem

class QProjectItem(QtGui.QTreeWidgetItem):
    """
    Верхний уровень меню, проекты
    """
    def __init__(self, root, parent, name):
        QtGui.QTreeWidgetItem.__init__(self, name)
        self._disabled = False
        self.root = root
        self.wrapper = parent

    def _build_menu(self, parent):
        """
        Context menu of table item, shows with right click
        """
        self.menu = QContextMenu(parent)
        self.menu._actions((
            ('Добавить таблицу', self._addTable),
            ('Переименовать', self._rename),
            ('Удалить', self._remove),
            ('Свойства', self._props),
            ('Модули', self._plugin),
            ('Экспорт в AMF', self._amf),
        ))

        self.menuPlugins = QContextMenu('Plugins', parent)
        self.menuHg = QContextMenu('Mercurial', parent)
        self.menuHg._actions((
            ("Обновить", self._hg_update),
            ("Зафиксировать", self._hg_commit)
        ))
        try:
            pth = os.path.join(self._project.data.path, 'scripts')
            self.menuPlugins._actions([
                (i.replace('.swf', ''), self._openHtml)
                for i in os.listdir(pth) if re.match('.*\.swf$', i)
            ])
            self.branches = QContextMenu(u'Переключить ветку', parent)
            self.branches._actions(
                [(i, self._hg_branch) for i in self._project.data.branches()]
            )
            self.menuHg.addMenu(self.branches)
        except:
            pass

        self.menu.addMenu(self.menuPlugins)
        self.menu.addMenu(self.menuHg)
        self._avaibility()
        return self.menu
 

    def _disable(self):
        """
        Имитируем отключение проекта,
        если не удалось проинициализровать его базу
        """
        self.setTextColor(0, QtGui.QColor('grey'))
        self._disabled = True
        self.root._message(self._project.error)

    def _avaibility(self):
        """
        Для неактивных проектов отключаем некоторые пункты контекстного меню
        """
        if self._disabled:
            for i in (self._amf, self._plugin, self._props, self._addTable):
                self.menu.avaibility[i].setDisabled(True)
            self.menuPlugins.setDisabled(True)
            self.menuHg.setDisabled(True)        
        
    def _props(self):
        """
        Свойства проекта
        """
        dialogue = ProjectProperty(self.root, self._project)
        dialogue.exec_()

    def _remove(self):
        """
        Удаляем проект из среды
        """
        dialog = EnsureDialog(
            self.root, self,
            u'''
            Удалить проект из среды?
            Данные на жестком диске не будут удалены
            ''',
            u'Удалить проект'
        )
        if dialog.exec_() == QtGui.QDialog.Accepted:
            item = self.root.tree.currentItem()
            projectManager.delProject(item._project.name)
            self.root._update()

    def _rename(self):
        """
        Простой диалог для переименования проекта
        влияет только на отображение в дереве
        """
        dialogue = InputDialugue(
            self.root, self, u'Новое имя', self._project.name
        )
        if dialogue.exec_() == QtGui.QDialog.Accepted:
            if not dialogue._val:
                return
            self.root.window.settings.setValue(
                "proj/%s/name" % dialogue._val,
                self.root.window.settings.value(
                    "proj/%s/name" % self._project.name, self._project.name
                ).toPyObject()
            )
            self.root.window.settings.remove(
                "proj/%s/name" % self._project.name
            )
            projectManager.renameProject(self._project.name, dialogue._val)
            self.root._update()
    
    # Таблицы

    def _addTable(self):
        """
        Добавляем новую таблицу 
        """
        dialogue = TableNewDialugue(self.root, self)
        if dialogue.exec_() == QtGui.QDialog.Accepted:
            self._project.data.create(
                dialogue._name,
                **dialogue._kwargs
            )
            new = QProjectTableItem(self.root, self, [str(dialogue._name)])
            new._project = self._project
            new._table = self._project.data.table[dialogue._name]
            self.addChild(new)

    # AMF

    def _amf(self):
        """
        Экспорт содержимого базы в AMF файл
        поддерживается загрузка на удаленный сервер
        """
        dialogue = AMFDialog(self.root, self._project)
        dialogue.exec_()

    # Плагины

    def _openHtml(self):
        """
        Открываем флеш плагин на отдельной вкладке,
        Поддержка общения flash <-> js <-> JsonDB через класс WebView
        """        
        swf = '%s' % self.root.tree._caction.text()
        pth = os.path.abspath(os.path.join(
            self._project.data.path, 'scripts', '%s.swf' % swf
        ))
        self.root.tab._addTab(
            pth,
            WebView(self.root, self, pth),
            '%s ()' % swf
        )

    def _plugin(self):
        """
        Немодальное окно диалога подключаемого python-модуля
        (находятся в папке path/to/db/scripts)
        """
        dialogue = PluginDialog(self.root, self._project)
        dialogue.show()

    # Mercurial

    def _hg_update(self):
        """
        Удобный диалог для
        hg pull & hg update -C
        """
        if HgDialogue(self.root, self, 'update').exec_() == QtGui.QDialog.Accepted:
            self.root._message(u'Wait. Идет обновление дерева проектов')
            self._project._load()
            self.root._update()
            self.root._message(u'Ready')

    def _hg_commit(self):
        """
        Удобный диалог для
        hg commit & hg push
        """
        HgDialogue(self.root, self, 'commit').exec_()

    def _hg_branch(self):        
        branch = '%s' % self.root.tree._caction.text()
        self.root._message("Wait")
        self._project.data.branch(branch)
        self.root._message("Project %s updated to branch %s" % (self._project.name, branch))
        self._project._load()
        self.root._update()

        