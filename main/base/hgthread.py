# -*- coding: utf-8 -*-
from PyQt4 import QtCore

class HgThread(QtCore.QThread):
    def __init__(self, root, parent, action, kwargs):
        self.root = root
        self.action = action
        self.kwargs = kwargs
        self.wrapper = parent
        self.kwargs['stdout'] = parent.stdout
        QtCore.QThread.__init__(self)

    def run(self):
        getattr(self.wrapper.wrapper._project.data, self.action)(**self.kwargs)
        self.sleep(1)
        self.wrapper._continue = False