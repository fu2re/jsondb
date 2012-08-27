from PyQt4 import QtCore
import json

class PluginBase(object):
    progress = 0.0

    def init(self, thread, jdb, params):
        self.thread = thread
        self._progress = 0.0
        self.kwargs = self.__kwargs__(params)
        self.db = jdb


    def __kwargs__(self, params):
        return dict([(k, self._g(k, v)) for k, v in params.items()])

    def _g(self, k, v):
        try: v = json.loads(v)
        except: pass
        try: return self.params[k](v)
        except: return v
        
    def out(self, val):
        self.thread.out(val)
        
    def progressed(self, val):
        self._progress += val
        self.thread.progressed(self._progress)

    def finish(self):
        self.thread.progressed(1)

    def exec_(self):
        self.run()
        self.finish()

    params = {
    }

    def run(self):
        pass

