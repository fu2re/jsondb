# coding: utf-8
import json

class Dive(object):
    __rvalue__ = {
        'int': int,
        'float': float,
        'list': json.loads,
        'dict': json.loads,
        'str': lambda x: x
    }


    def __init__(self, target, template, value='', object=None):
        self.map = target.split('.')
        self.value = value
        self.template = template
        self.object = object
        self.core = object.core
        

    def set(self, obj):
        self.istemplate = obj == self.template
        if self.value is None:
            return obj        
        return self.__deeper__(obj, self.value)

    def get(self, obj):
        return self.__get__(obj, self.map)

    def remove(self, obj):
        self.istemplate = obj == self.template
        key = self.map[-1]
        self.map = self.map[:-1]
        data = self.__get__(obj, self.map)
        try:
            result = data[key]
            del data[key]
        except:
            result = data[int(key)]
            del data[int(key)]
        self.__deeper__(obj, data)
        
        return result

    # PRIVATE

    def __deeper__(self, obj, data):
#        data = self.__value_type__(self.value)
        doc = obj
        for index, key in enumerate(reversed(self.map)):
            map = self.map[:-index-1]
            obj = self.__get__(doc, map, True)
            obj = self.__exset__(obj, map, key, data)
            data = obj
        return obj

    def __get__(self, data, map, imitate=False):
        for i in map:
            try:
                data = data[i]
            except:
                try:
                    data = data[int(i)]
                except:
                    if imitate:
                        data = self.__create__(map)
                    else:
                        try:
                            data = data['$items']
                        except:
                            return None
        return data


    def __create__(self, map):
        target = '.'.join(map)
        try:
            return self.object.__create__(target)
        except:
            raise NameError('Wrong address %s' % target)

    def __recursy_set__(self, obj, map, key, value):
        while len(obj) < key+1:
            obj.append(self.__create__(map+['0']))
        obj[key]=value
        return obj

    def __exset__(self, obj, map, key, value):
        kind = self.object.__field__('.'.join(map)).kind
        if kind == 'list' and not self.istemplate:
            return self.__recursy_set__(obj, map, int(key), value)
        else:
            obj[key] = value
            return obj

