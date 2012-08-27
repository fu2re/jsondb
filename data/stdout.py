class FakeStdout(object):
    lines = []
    def write(self, text):
        self.lines.append(text.decode('utf-8'))

    def readline(self):
        if self.lines:
            return self.lines.pop(0)
#        else:
#            return ''

    def readlines(self):
        while self.lines:
            yield self.readline()

    def read(self):
        a = ''.join(self.readlines())
        return a

    def close(self):
        del self