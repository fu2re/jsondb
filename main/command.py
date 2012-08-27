# -*- coding: utf-8 -*-
import sys
import logging
import traceback
import datetime

from PyQt4 import QtCore, QtGui, Qt
from window import QMainWindow
from data.projects_manager import projectManager
from main.dialogue.project_add_dialog import ProjectAddDialog
from main.dialogue.project_create import ProjectCreateDialog
from main.form.tree.wrapper import QProjectTree
from main.form.tree.table import QProjectTableItem
from main.form.tab import Tab
from main.form.table.wrapper import QBox
from main.form.document.wrapper import QDoc
from main.dialogue.global_settings import SettingsDialugue

def statused(f):
    def w(object, *args, **kw):
        object.root.window.statusbar.showMessage('Busy')
        rs = f(object, *args, **kw)
        object.root.window.statusbar.showMessage('Ready')
        return rs
    return w

class Command(object):
    """
    Construction class
    Собирает и компанует виджеты
    Обработка глобальных команд с клавиатуры происходит тут
    """
    boldFont = QtGui.QFont()
    boldFont.setBold(True)
    changed = []
    added = []
    logger = logging.getLogger('jsondb_explorer')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler('err.log'))

    def setupUi(self, window):
        self.window = window
        window.root = self
        self.root = self
        self.stg = self.window.settings
        self.window._set_title("JsonDB Explorer")
#        self.api = {}        
        
        self.tree = QProjectTree(self, self.window)
        self.tree.itemDoubleClicked.connect(self._openTable)

        self.tab = Tab(self.window)
        self.window.cpanel.addWidget(self.tree)
        self.window.cpanel.addWidget(self.tab)


        self.window.main.restoreState(self.stg.value("main/state/v").toByteArray())
        self.window.cpanel.restoreState(self.stg.value("main/state/h").toByteArray())
        projectManager.update(
            self.stg.value("acc/key").toPyObject(),
            self.stg.value("acc/remote").toPyObject()
        )
        self.window._build_menu('&Файл', (
            ("Создать проект", self.createProject, None),
            ("Добавить проект", self.addProject, None),
            ("Save", self._save, 'Ctrl+S'),
            ("Выход", self.window._on_exit, None)
        ))
        self.window._build_menu('Вид', (
            ("Закрыть все вкладки", self.tab._removeAll, 'Ctrl+Shift+W'),
        ))
        self.window._build_menu('Сервис', (
            ("Настройки", self._props, None),
        ))
        
        self._update()

    def _props(self):
        """
        Глобальные настройки среды
        """
        dialogue = SettingsDialugue(self)
        dialogue.exec_()

    def _save(self):
        """
        Сохранение всех изменений в среде
        Активируется нажатием Ctrl+S
        """
        for obj in self.changed:
            obj.save()
        self.changed = []
        self.window.statusbar.save.setVisible(False)

    # Манипулируем вкладками
#    @statused
    def _openTable(self, it=None):
        """
        открываем выбранную таблицу на новой вкладке
        """        
        if isinstance(self.tree.currentItem(), QProjectTableItem):
            self.tab._addTab(
                it._table,
                QBox(it._project.name, it._table.name, it._table, self),
                it._table.name
            )
    @statused
    def _openDocument(self, id, table, project_name):
        """
        Открывает документ в новой вкладке
        Метод вызывается в self.tree.ProjectTableItem и table.item,
        поэтому вынесен в root level
        """
        content = QDoc(project_name, table.name, table, id, self)
        self.tab._addTab(
            content.doc,
            content,
            "%s (%s)" % (id, table.name)
        )     

    # Действия над проектами
    @statused
    def addProject(self):
        """
        Подключает новый проект из указанной папки
        """
        prAdd = ProjectAddDialog(self.window)
        if prAdd.exec_() == QtGui.QDialog.Accepted:
            self._update()

    @statused
    def createProject(self):
        """
        Создаем новый проект в указанной папке
        """
        prAdd = ProjectCreateDialog(self.window)
        if prAdd.exec_() == QtGui.QDialog.Accepted:
            self._update()

    def _update(self):
        """
        Метод нужен для того чтобы можно было присовить
        сигналы дочерним объектам, во время инициализации
        """
        self.tree._update()


    # Список изменения, нужен для корректного сохранения

    def _changed(self, obj):
        """
        При внесении изменений на страницу(вкладку)
        нужен для исключительно для сохранения
        """
        if obj not in self.changed:
            self.changed.append(obj)
            self.window.statusbar.save.setVisible(True)

    def _dy_changed(self, obj):
        """
        При внесении изменений в объект
        В отличие от _changed - нужен для исключительно для отрисовки
        """
        if obj not in self.added:
            self.added.append(obj)
            
    def _dy_unchanged(self, obj):
        """
        метод автоматически вызывается при отрисовке страницы,
        удаляет указаный объект из списка GUI изменений
        Если объект присутствует в списке у вызываеющего объекта
        будет вызвано обновление содержимого
        """
        changed = obj in self.added
        if changed:
            self.added.remove(obj)
        return changed

    def _unchanged(self, obj):
        """
        Список автоматически очищается при вызове сохранения
        """
        if obj in self.changed:    
            self.changed.remove(obj)

    def _log(self, message=None, text=None):
        """
        Доюавляем в лог сообщение message,
        Выводим в статусбар сообщение о вызванном исключении
        """
        self.logger.info(text or traceback.format_exc())
        self._message(message or str(sys.exc_info()[1]))
        

    def _message(self, text):
        self.window.act.insertPlainText(u'%s: %s\r' % (
            datetime.datetime.now().strftime("%y.%m.%d %H:%M"),
            text
        ))

    def _getaddr(self, *args):
        return '.'.join([str(i) for i in args if i not in (None, '')])

def init():
    """
    Инициализация приложения
    создаем отдельный, независимый объект окна
    и прогоняем его через класс комманд
    """
    app = QtGui.QApplication(sys.argv)
    MainWindow = QMainWindow()
    form = Command()
    form.setupUi(MainWindow)
    return app, form, MainWindow