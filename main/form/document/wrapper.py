# -*- coding: utf-8 -*-
import json
import sys
import traceback
from PyQt4 import QtCore, QtGui, Qt
from main.window import uni
from data.projects_manager import projectManager
from main.base.contextMenu import QContextMenu
from main.dialogue.template_add_field import FieldAddDialog

from table import QDocTable
from tree import QDocTree
from tree_item import QItem
from table_combobox import QComboTable
from main.base.QRemoteImage import QRemoteImage

class RightPan(QtGui.QSplitter):
    def __init__(self, root, wrapper):
        QtGui.QSplitter.__init__(self, QtCore.Qt.Vertical)
        self.addWidget(wrapper.doctable)
        self.raw = QtGui.QPlainTextEdit()
        self.raw.setReadOnly(True)
        self.addWidget(self.raw)
        

class QDoc(QtGui.QSplitter, uni):
    def __init__(self, project_name, table_name, table, id, root):
        self.project_name = project_name
        self.table_name = table_name
        self.table = table
        self.doc = self.table.get(id)
        self.root = root
        QtGui.QSplitter.__init__(self)

        self.tree = QDocTree(root, self)
        self.doctable = QDocTable(root, self)
        self.addWidget(self.tree)
        self.rpanel = RightPan(self.root, self)
        self.addWidget(self.rpanel)

        self.tree.itemClicked.connect(self._editDocument)
        self.doctable.itemChanged.connect(self._memSave)
        self.splitterMoved.connect(self._saveState)
        self.restoreState(self.root.stg.value("doc/state").toByteArray())
        self.rpanel.restoreState(self.root.stg.value("doc/rpanel/state").toByteArray())

        
    def _update(self, *args):
        """
        Обновляем содержимое вкладки,
        если была изменена структура таблицы, или сам документ
        """
        if self.root._dy_unchanged(self.table) or not hasattr(self, 'firstshow'):
            self.tree._update()
            if not self.tree.currentItem():
                self.tree.setCurrentItem(self.tree.topLevelItem(0))
                
            self._editDocument()
            self.firstshow = True

    def _saveState(self):
        """
        Сохраняем геометрию вкладки
        """
        self.root.stg.setValue("doc/state", self.saveState())
        self.root.stg.setValue("doc/rpanel/state", self.rpanel.saveState())

    def _editDocument(self, item=None):
        """
        Заполняем таблицу по текущему элементу дерева
        """
        item = item or self.tree.currentItem()
        self.doctable._fill(item)
        self.rpanel.raw.setPlainText(u'%s' % json.dumps(item._data, ensure_ascii=False, indent=4))


    def _memSave(self, item):
        """
        При изменении в модели сохраняем модель в память
        Актуально только после инициализации
        """
        if not hasattr(item, '_activated'):
            return

        self.root._changed(self.doc)
        self.root._dy_changed(self.table)
        if hasattr(item, '_fieldName'):
            newname = '%s' % item.text()
            self.doc.__move__(
                self.root._getaddr(item._row._addr, item._fieldName),
                self.root._getaddr(item._row._addr, newname),
                commit= False
            )
            item._fieldName = newname

        else:
            if not isinstance(item, QComboTable) and not \
            isinstance(item, QRemoteImage):
                item._val = '%s' % item.text()

            try:
                target = self.root._getaddr(item._row._addr, item._field._fieldName)
                if item._val == '' and self.table.structure(target)['$format'].get('blank'):
                    self.doc.remove(target)
                else:
                    self.doc.set(
                        target,
                        self._get_val(item),
                        False
                    )

            except (UnicodeEncodeError, ValueError):
                self.root._message(
                    u'Ошибка типа значения, пожалуйста укажите значение соответствующего типа'
                )

            except:
                self.root._log()

        self.tree._update()
        self._editDocument(self.tree.currentItem())
            

    def _get_val(self, item):
        """
        Возвращает конвертированное в соответствии
        с шаблоном значение поля(новое)
        """
        kind = self.table.__kind__(
            self.root._getaddr(item._row._addr, item._field._fieldName)
        )
        return projectManager.converter[kind](item._val)

    def save(self):
        """
        Сохраняем всеменения из памяти базы на жесткий диск
        """
        if self.doc in self.root.changed:
#            index = self.root.tab.tabBar().currentIndex()
#            self.root.tab.tabBar().setTabText(index,
#                re.sub('\*$', '', unicode(self.root.tab.tabBar().tabText(index)))
#            )
            self.root.changed.remove(self.doc)
            self.doc.save()