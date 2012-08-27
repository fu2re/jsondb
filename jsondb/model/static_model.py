# coding: utf-8

class StaticModel():
    def __init__(self, is_list=False):
        self.is_list = is_list
        self.fields = {}
        self.items = []


    def addField(self, model, field):
        if not self.is_list:
            self.fields[field] = model


    def addItem(self, model):
        if self.is_list:
            self.items.append(model)

    @property
    def data(self):
        if self.is_list:
            data = []
            for key in self.items:
                data.append(self.items)
            return data
        else:
            data = {}


if __name__ == '__main__':
    pass

    model = StaticModel()
    model.addField(StaticModel(), 'test')

    print model
