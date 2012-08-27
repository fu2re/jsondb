from utils.lazy import lazy_property

class Field(object):
    def __init__(self, core, pattern, target, value=None):
        self.core = core
        self.pattern = pattern
        self.target = target
        if not pattern:
            raise KeyError("Wrong target %s" % target)

    @property
    def format(self):
        return self.pattern['$format']

    @property
    def kind(self):
        return self.core.__kind__(self.format)

    @property
    def blank(self):
        return True if self.format.get('blank') else False

    @property
    def text(self):
        return self.format.get('text')

    @property
    def min(self):
        return self.format.get('min')

    @property
    def max(self):
        return self.format.get('max')

    @property
    def foreign(self):
        return self.format.get('foreign_key')

    @property
    def default(self):
        return self.format.get('default')

    @property
    def values(self):
        return self.format.get('values')

    @property
    def is_file(self):
        return self.format.get('is_file')

    @property
    def compressed(self):
        return not bool(self.format.get('nocompress'))

    @lazy_property
    def items(self):
        if '$items' in self.pattern:
            return Field(
                self.core,
                self.pattern['$items'],
                '.'.join((self.target, '$items')))

    @property
    def keys(self):
        return dict([
            (k, v) for k, v in self.pattern.items()
            if k not in ('$format', '$items')
        ])

#    def update(self, ):
