# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import urllib
import hashlib
import os
import re

class WebThread(QtCore.QThread):
    def __init__(self, root, parent):
        self.root = root
        self.wrapper = parent
        self.queue = parent.queue
        QtCore.QThread.__init__(self)

    def _get_remote(self, addr, path):
        if re.match("[A-Za-z0-9]*/[A-Za-z0-9]{32}", addr):
            addr = 'http://%s/%s' % (
                self.wrapper.wrapper.table.core.remote_static_server, addr
            )
        urllib.urlretrieve(addr, path)

    def run(self):
        while True:
            if self.queue.empty():
                break
            addr, item = self.queue.get()
                
            remote = False
            if addr.split('.')[-1] in ('png', 'jpg', 'jpeg'):
                name = hashlib.md5(addr).hexdigest()
                path = os.path.join('temp', name)
                if name not in os.listdir(os.path.abspath('temp')):
                    remote = True
                    self._get_remote(addr, path)
                    
                val = path
                ispix = True
            else:
                val = addr or '<empty field>'
                ispix = False

            self.emit(
                QtCore.SIGNAL(
                    "taskDone(PyQt_PyObject, bool, QString, bool)"),
                    item, ispix, val, remote
                )
            self.queue.task_done()