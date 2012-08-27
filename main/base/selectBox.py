# -*- coding: utf-8 -*-
from PyQt4 import QtGui

class QSelectBox(QtGui.QComboBox):
    def standart(self, value=None):        
        self.addItem('No', 0)
        self.addItem('Yes', 1)
        try:
            self.setCurrentIndex(int(value))
        except:
            pass        