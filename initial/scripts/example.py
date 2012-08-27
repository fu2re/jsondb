from plugins import PluginBase

class Plugin(PluginBase):
    """
    Simple example of jdb module

    Attributes
    >>> self.kwargs # Params given to the script through interface
    >>> self.db # JsonDB object

    Usage
    Define all used params in self.params
    Define main cycle in self.run method

    Note that this module must not contain any imports
    """
    params = {
        'str':str,
        'int':int,
        'list':list,
        'custom':lambda x: pow(x) + x/2
    }

    def run(self):
        while self._progress < 1:
            self.out('Current progress: %s' %  self._progress)
            self.progressed(0.01) # Use this method to update progress bar in Explorer

