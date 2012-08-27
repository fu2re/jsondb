# -*- coding: utf-8 -*-
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import traceback
from data.projects_manager import projectManager

class WebWidget(QWidget):

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(Qt.white)
        painter.setPen(Qt.black)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.width()/4, self.height()/4,
                         self.width()/2, self.height()/2)
        painter.end()

    def sizeHint(self):
        return QSize(100, 100)


class WebPluginFactory(QWebPluginFactory):

    def __init__(self, parent = None):
        QWebPluginFactory.__init__(self, parent)

    def create(self, mimeType, url, names, values):
        if mimeType == "x-pyqt/widget":
            return WebWidget()

    def plugins(self):
        plugin = QWebPluginFactory.Plugin()
        plugin.name = "PyQt Widget"
        plugin.description = "An example Web plugin written with PyQt."
        mimeType = QWebPluginFactory.MimeType()
        mimeType.name = "x-pyqt/widget"
        mimeType.description = "PyQt widget"
        mimeType.fileExtensions = []
        plugin.mimeTypes = [mimeType]
        print "plugins"
        return [plugin]
    
class JSIntarface():
    def __kwargs__(self, *args):
        for i in args:
            yield u'%s' % i



class WebView(QWebView, JSIntarface):
    def __init__(self, root, parent, plugin):
        f = open('plugin.html', 'r')
        html = f.read()
        f.close()

        self.root = root
        self.wrapper = parent
        QWebView.__init__(self, self.root.window)
        self.db = self.wrapper._project.data
        self.r = None
#        a = StupidClass(self.wrapper._project.data)
        self.page().mainFrame().addToJavaScriptWindowObject("py", self)

        self.setHtml(html % (os.path.abspath('jq.js'), plugin))


        self.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        websettings = self.settings()
        websettings.setAttribute(QWebSettings.PluginsEnabled,True)
#        websettings.setAttribute(QWebSettings.LocalStorageEnabled, True)
#        websettings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)

    @pyqtProperty(str)
    def data(self):
        return self.db.data(True)
    
    
    @pyqtSlot(str, str, str, str)
    def jdbSet(self, table, id, target, value):
        try:
            table, target, value, id = self.__kwargs__(table, target, value, id)
            t = self.db.table[table]
            d = t.get(id)
            d.set(self.__convert(d, target, value), False)
            self.r = True
            self.__changed__(d, t)
        except:
            self.r = str(sys.exc_info()[1])

    @pyqtSlot(str, str, str, str, str)
    def jdbAdd(self, table, id, target, value, key):
        try:
            table, target, value, key, id = self.__kwargs__(table, target, value, key, id)
            t = self.db.table[table]
            d = t.get(id)
            if d.__field__(target).kind == 'list' and key: key = int(key)
            v = self.__convert(d, '.'.join((target, '$items')), value)
            d.add(target, v, key, False)
            self.__changed__(d, t)
            self.r = True
        except:
            self.r = traceback.format_exc()

    @pyqtSlot(str, str, str, str, str)
    def jdbSwitch(self, table, id, target, key, terminate):
        try:
            table, target, key, terminate, id = self.__kwargs__(table, target, key, terminate, id)
            t = self.db.table[table]
            d = t.get(id)
            if d.__field__(target).kind == 'list': key, terminate = int(key), int(terminate)
            d.switch(target, key, terminate, False)
            self.__changed__(d, t)
            self.r = True
        except:
            self.r = traceback.format_exc()

    @pyqtSlot(str, str, str)
    def jdbRemove(self, table, id, target):
        try:
            table, target, id = self.__kwargs__(table, target, id)
            t = self.db.table[table]
            d = t.get(id)
            self.r = d.remove(target, False)
            self.__changed__(d, t)
        except:
            self.r = traceback.format_exc()

    @pyqtSlot(str, str)
    def jdbDelete(self, table, id):
        try:
            table, id = self.__kwargs__(table, id)
            t = self.db.table[table]
            d = t.get(id)
            d.delete()
            self.r = True
            self.__changed__(d, t)
        except:
            self.r = traceback.format_exc()

    @pyqtSlot(str)
    def jdbCreate(self, table):
        try:
            table, = self.__kwargs__(table)
            t = self.db.table[table]
            d = t.new(False)
            self.r = d.id
            self.__changed__(d, t)
        except:
            self.r = traceback.format_exc()

    @pyqtSlot(str, str, str)
    def jdbGet(self, table, id, target):        
        try:
            table, target, id = self.__kwargs__(table, target, id)
            self.r = self.db.table[table].get(id).get(target)
        except:
            self.r = traceback.format_exc()

    @pyqtProperty(str)
    def result(self):
        """Return the Python version."""
        return self.db.core.encoder(self.r)

    # PRIVATE

    def __changed__(self, doc, table):
        self.root._changed(doc)
        self.root._dy_changed(table)

    def _update(self):
        pass

    def __convert(self, doc, target, value):        
        return projectManager.converter[doc.__field__(target).kind](value)

#def GetWidget(html):
#    view = QWebView()
##    factory = WebPluginFactory()
##    view.page().setPluginFactory(factory)
#    view._update = update
#    view.setHtml(html)
#    return view