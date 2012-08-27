# coding: utf-8
import re
import os

from PyQt4 import QtGui, QtCore
from main.window import uni
from __resizable__ import Resizable

class QTableProperty(QtGui.QDialog, uni, Resizable):
    def __init__(self, project_name, table_name, table, root):
        self.root = root
        self.table = table
        self.project_name = project_name
        self.table_name = table_name
        self.path = os.path.join(self.table.core.path, 'parser')

        QtGui.QDialog.__init__(self)
        self.visible_fields = self.settings.value(
            "project/%s/%s/visible" % (self.project_name, self.table_name),
            []
        ).toList()
        self.fast_fields = self.table.__get_settings__("fast_fields") or []

        self.main = QtGui.QTabWidget(self)
        self.setWindowTitle(u'Настройки таблицы')
        self.grid = QtGui.QGridLayout()
        self._restoreGeom('dialog/tableprop/geometry', 400, 400)
        
        self.btnOk = QtGui.QPushButton(u'Ok')
        self.btnClose = QtGui.QPushButton(u'Отмена')

	self.btnClose.clicked.connect(self.reject)
        self.btnOk.clicked.connect(self._confirm)
        
        self.main.addTab(self._Fields(), u'Вид')
        self.main.addTab(self._FastFields(), u'Быстрые поля')
        self.main.addTab(self._Parser(), u'Парсер')
        self.grid.addWidget(self.main, 0, 0)
        self.grid.addWidget(self.btnOk, 1, 0)
        self.grid.addWidget(self.btnClose, 1, 1)

        self.setLayout(self.grid)

#        self.setGeometry(QtCore.QRect(400,400,500,500))
        
    def _confirm(self):
        self.table.__set_parser__('%s' % self.cb.currentText())
        self.settings.setValue(
            "project/%s/%s/visible" % (self.project_name, self.table_name),
            self._parseFields(self.model)
        )
        self.table.__set_fast_fields__(self._parseFields(self.fmodel))
        self.accept()

    def _parseFields(self, model):
        result = []
        while True:
            item = model.takeRow(0)
            if not item:
                return result
            if item[0].checkState() == 2:
                result.append('%s' % item[0].text())

    def _Parser(self):
        w = QtGui.QWidget()
        wl = QtGui.QFormLayout()
        self.cb = QtGui.QComboBox()
        self.cb.addItem('')
        try:
            choices = [
                k.replace('.py', '') for k in os.listdir(self.path)
                if re.search('.py$', k)
            ]
            self.cb.addItems(choices)
            self.cb.setCurrentIndex(
                choices.index(self.table.__get_parser_name__())+1
            )
        except:
            pass
        wl.addRow(u'Скрипт:', self.cb)
        w.setLayout(wl)
        return w

    def _Fields(self):
        w = QtGui.QWidget()
        wl = QtGui.QHBoxLayout()
#        wl = QtGui.QFormLayout()
        self.list = QtGui.QListView(self)
        self.model = QtGui.QStandardItemModel()
        self._fill(self.model, self.list, self.visible_fields)

        wl.addWidget(self.list)
        w.setLayout(wl)
        return w
           
    def _FastFields(self):
        w = QtGui.QWidget()
        wl = QtGui.QHBoxLayout()
        self.flist = QtGui.QListView(self)
        self.fmodel = QtGui.QStandardItemModel()
        self._fill(self.fmodel, self.flist, self.fast_fields)

        wl.addWidget(self.flist)
        w.setLayout(wl)
        return w

    def _fill(self, model, _list, attr):
        fields = sorted(self.table.simple_fields())
        for i in fields:
            if i != '':
                item = QtGui.QStandardItem(i) #QCheckBox(i, self)
                check = QtCore.Qt.Checked if i in attr else QtCore.Qt.Unchecked
                item.setCheckState(check)
                item.setCheckable(True)
                model.appendRow(item)

#            self.grid.addRow(cbox)
        _list.setModel(model)
        return
#        self.show()
#        self.scroll.setWidget(self)
#        self.scroll.show()

#        self.scroll.setLayout(self.grid)
#        self.box.addWidget(self.scroll)
#        self.setLayout(self.box)