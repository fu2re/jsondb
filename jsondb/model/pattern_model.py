import json

def encode_json(model):
    data = model.getDict()
    json_string = json.JSONEncoder(ensure_ascii=False, indent=4, sort_keys=True).encode(data)
    return json_string


def decode_json(json_string):
    data = json.JSONDecoder().decode(json_string)
    model = PatternModel(**data['$format'])
    model.setDict(data)
    return model


def encode_dict(model):
    data_dict = model.getDict()
    return data_dict


def decode_dict(data_dict):
    model = PatternModel(**data_dict['$format'])
    model.setDict(data_dict)
    return model


class PatternModel():

    DICT = 'dict'
    LIST = 'list'
    INT = 'int'
    STR = 'str'
    UNICODE = 'unicode'

    params = [  'kind', 'blank', 'max', 'min',
                'default', 'dynamic', 'values', 'text',
                'foreign_key']


    defaults = {
        'dict': {'dynamic': 0},
        'list': {},
        'int': {'default':0},
        'float': {'default':0.0},
        'str': {'text':''}
    }

    def __init__(self, kind=DICT, **kwargs):

        self.kind = kind
        self.blank = None
        self.fereign_key = None
        self.is_file = None
        self.min = None
        self.max = None
        self.default = None
        self.dynamic = None
        self.values = None
        self.nocompress = None
        self.text = ''

        self.process_default()
        self.process_kwargs(kwargs)

        self.params = PatternModel.params

        self.fields = {}


    def process_kwargs(self, params):
        for param in params:
            if hasattr(self, param):
                setattr(self, param, params[param])


    def process_default(self):
        self.process_kwargs(PatternModel.defaults[self.kind])


    def getDict(self):
        data = { '$format': {} }
        for key in self.params:
            if hasattr(self, key) and not getattr(self, key) in [None]:
                data['$format'][key] = getattr(self, key)

        for field in self.fields:
            data[field] = self.fields[field].getDict()
        return data


    def setDict(self, data):
        for key in data:
            if not key in ['$format']:
                format = data[key]['$format']
                model = PatternModel(**format)
                model.setDict(data[key])
                self.add(model, key)


    def add(self, model, field=None):
        if self.kind == PatternModel.LIST:
            field = '$items'
        self.fields[field] = model

def execute():
    a = PatternModel()
    coordinates = PatternModel('list')
    map = PatternModel('list')
    public = PatternModel('int')
    theme = PatternModel('int')
    level = PatternModel('int')
    texts = PatternModel()
    ru = PatternModel()
    texts.add(ru, 'ru')

    a.add(coordinates, 'coordinates')
    a.add(map, 'map')
    a.add(public, 'public')
    a.add(theme, 'theme')
    a.add(level, 'level')
    a.add(texts, 'texts')

    print a.getDict()