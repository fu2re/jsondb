# coding: utf-8
import re
import string

class QuerySet( list ):
    convert = {
        'int':int,
        'float':float,
        'str':lambda x: x.encode('utf-8')
    }

    # BASIC METHODS

    def __init__(self, table, container=None):
        if container is None:
            container = []
        self.container = container
        self.t = table
        self.core = table.core

    def __str__(self):
        return str(self.container)

    def __repr__(self):
        return self.container

    def __getitem__(self, key):
        return self.container[key]

    def __iter__(self):
        for i in self.container:
            yield i

    def __getslice__(self, i=None, j=None):
        return self.container[i:j]

    def __len__(self):
        return len(self.container)

    def get(self, key):
        return self.container.get[key]

    def order_by(self, target, reverse = False):
        """
        Order items by field
        """
        if re.search('^-', target):
            target = re.sub('^-', '', target)
            reverse = True

        result = sorted([(i.get(target), i) for i in self.container])

        if reverse:
            result.reverse()

        self.container = [v for k,v in result]
        return self

    def exclude(self, target, value):
        original = self.container
        a = self.filter(target,value).container
            
        self.container = [i for i in original if i not in a]
        return self

    def filter(self, target, value):
        ef = {
            'in':self.__filter_in__,
            'gt':self.__filter_gt__,
            'lt':self.__filter_lt__,
            'haskey':self.__filter_haskey__,
            'contains':self.__filter_contains__,
            'icontains':self.__filter_icontains__
        }

        for k, v in ef.items():
            if re.search('__%s$' % k, target):
                v(re.sub('__%s$' % k, '', target), value)
                return self

        self.__filter_simple__(target, value)
        return self

    
    @property
    def view(self):
        return [i.__item__ for i in self.container]

    def __kind__(self, target):
        if not hasattr(self, '_kind'):
            self._kind = self.t.__kind__(target)
        return self._kind

    # EXTENDED FILTERS

    def __filter_in__(self, target, value):
        r = []
        for item in self.container:
            v = item.get(target)
            if not v is None:
                if self.convert[self.__kind__(target)](v) in value:
                    r.append(item)
        self.container = r
#        del self._kind

    def __filter_contains__(self, target, value):
        kind =  self.__kind__(target)
        wxfilter = {
            'list':lambda value, item: value in item.get(target),
            'dict':lambda value, item: value in item.get(target).values(),
            'ddict':lambda value, item: value in item.get(target).values(),
            'str':lambda value, item: string.find(item.get(target).encode('utf-8'), value) != -1
        }
        self.container = [
            item for item in self.container if wxfilter[kind](value, item)
        ]
        del self._kind


    def __filter_icontains__(self, target, value):
        value = value.decode('utf-8').lower().encode('utf-8')
        self.container = [
            item for item in self.container
            if item.get(target).lower().encode('utf-8').find(value) != -1
        ]

    def __filter_lt__(self, target, value):
        self.container = [item for item in self.container if item.get(target) < value]

    def __filter_gt__(self, target, value):
        self.container = [item for item in self.container if item.get(target) > value]

    def __filter_haskey__(self, target, value):
        exist = lambda item, v: item.exist(self.core.__target__(target, v))
        if type(value) in (list, dict):
            r = []
            for v in value:
                r.extend([item for item in self.container if exist(item, v) and item not in r])
            self.container = r
        else:
            self.container = [item for item in self.container if exist(item, value)]

        
#        del self._kind
    def __filter_simple__(self, target, value):
        self.container = [item for item in self.container if item.__filter__(target, value)]