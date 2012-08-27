# coding: utf-8
from PyQt4 import QtCore, QtGui, Qt
from main.window import uni

class QContextMenu(QtGui.QMenu, uni):
    """
    Контекстное меню
    """
    def _actions(self, actions):
        self.avaibility={}
        for i in actions:
            action = self.addAction(self._to_utf(i[0]))
            action._action = i[1]
            self.avaibility[action._action] = action
#        self.avaibility = dict([(v, k) for k,v in self.actions.items()])

    def _do(self, action):
        if action:
            action._action()
#            return self.actions[action]()