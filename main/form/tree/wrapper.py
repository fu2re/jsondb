# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, Qt
from project import QProjectItem
from table import QProjectTableItem
from data.projects_manager import projectManager

class QProjectTree(QtGui.QTreeWidget):
    """
    Левая панель, дерево вида:
    проект -> таблица
    """
    def __init__(self, root, parent):
        QtGui.QTreeWidget.__init__(self, parent)
        self.root = root
        self.setHeaderLabel(u'Проекты')

    def _currentItem(self):
        item = self.currentItem()
        if not item:
            item = self.topLevelItem(0)
        elif item.parent():
            item = item.parent()
        return item

    def contextMenuEvent(self, event):
        """
        Context menu of project item, shows with right click
        """
        item = self.itemAt(event.pos())
        if item:
            menu = item._build_menu(self)
            self._caction = menu.exec_(self.mapToGlobal(event.pos()))
            menu._do(self._caction)

    def _update(self):
        """
        Обновляет данные о проектах и их таблицах
        перестраивает их отображение
        """
        self.clear()
        for project in projectManager.projects:
            try:
                name = '%s [%s]' % (project.name, project.data.summary()[0])
            except:
                name = project.name
            item = QProjectItem(self.root, self, [name])
            item._project = project
            if not hasattr(project, 'data'):
                item._disable()
            elif not project.data:
                item._disable()
            else:
                project.data.project_name = self.root.stg.value(
                    "proj/%s/name" % project.name, project.name
                ).toPyObject()
                for k, v in project.data.table.items():
                    table = QProjectTableItem(self.root, self, [str(k)])
                    table._table = v
                    table._project = project
                    item.addChild(table)
                    self.addTopLevelItem(item)
            self.show_warnings(project)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def show_warnings(self, project):
        for table_name, table_errors in project.data.errors.items():
            for doc_id, doc_errors in table_errors.items():
                for error in doc_errors:
                    self.root._message('WARNING: Document %s.%s has error in field %s' % (table_name, doc_id, error))