from PyQt4 import QtCore
class Resizable(object):
    def _saveGeom(self):
        self.root.window.settings.setValue(
            self.pathToSettingsGeom, QtCore.QVariant(self.geometry())
        )

    def _restoreGeom(self, settings, *initial):
        self.pathToSettingsGeom = settings
        rect = self.root.window.settings.value(
            settings, None
        ).toRect()
        if rect:
            self.setGeometry(rect)
        else:
            self.resize(*initial)


    def resizeEvent(self, event):
        self._saveGeom()
#        self.output.setMinimumHeight(max(self.height()-130, 194))
#        Step.resizeEvent(self, event)

    def moveEvent(self, event):
        self._saveGeom()
#        Step.moveEvent(self, event)