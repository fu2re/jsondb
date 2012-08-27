# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import urllib
import hashlib
import os
from main.base.contextMenu import QContextMenu
from main.dialogue.upload import UploadDialugue
from main.dialogue.input import InputDialugue

class QRemoteImage(QtGui.QLabel, QtGui.QTableWidgetItem):
    """
    Виджет позволяющий вставить изображение с удаленного сервера в таблицу
    использует кеш
    """
    def __init__(self, root, parent, addr):
        self.root = root
        self.wrapper = parent
        QtGui.QLabel.__init__(self)
        self.addr = addr
        
#        self.connect(self.thread, QtCore.SIGNAL('finished()'), self._get_finished)
#        self.connect(self.thread, QtCore.SIGNAL('taskDone()'), self._get_finished, QtCore.Qt.QueuedConnection)
        self.wrapper.queue.put((addr, self))
        
    def _buildMenu(self, parent):
        self.menu = QContextMenu(parent)
        self.menu._actions((
            ('Изменить адрес', self._specify),
            ('Загрузить с компьютера', self._upload),
        ))
        return self.menu

    def contextMenuEvent(self, event):
        menu = self._buildMenu(self)
        action = menu.exec_(self.mapToGlobal(event.pos()))
        menu._do(action)

    # поток

    def _get(self, addr):
        """
        запускаем поток получающий изображение
        """
        self.wrapper.queue.put((addr, self))
        self.wrapper.thread.start()

    def _get_finished(self, ispix, val, remote):
        """
        Вставляет изображение
        Вызывается при завершении текущей задачи в очереди.
        """
        if ispix:
            self.setPixmap(QtGui.QPixmap(val))
        else:
            self.setText(val)
        if remote:
            self.wrapper.resizeColumnsToContents()
            self.wrapper.resizeRowsToContents()

    # редактирование
    
    def _specify(self):
        """
        позволяет изменить текущий url
        указав адрес на удаленном сервере
        """
        dialogue = InputDialugue(self.root, self.wrapper, u'Укажите Url', initial=self.addr)
        if dialogue.exec_() == QtGui.QDialog.Accepted:
            self._val = dialogue._val
            self.wrapper._memSave(self)
#            self._get(self._val)

    def _upload(self):
        """
        позволяет изменить текущий url
        загрузив изображение с локальной машины
        """
        dialogue = UploadDialugue(self.root, self.wrapper)
        if dialogue.exec_() == QtGui.QDialog.Accepted:
            status = dialogue._resp.get('status')
            self.root.window.statusbar.showMessage(
                status or "Coudn't connect to server"
            )
            if status == 'Success':
                self._val = dialogue._resp['result']['relative']
                self.wrapper._memSave(self)
#                self._get(self._val)


    def toPyObject(self):
        return self
