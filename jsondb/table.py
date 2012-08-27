# coding: utf-8
import os
import re
import codecs

#from django.shortcuts import render_to_response
#from django.core.paginator import Paginator
from copy import copy
from field import Field
from checks import Check
from document import Document
from queryset import QuerySet
from utils.dive import Dive
from utils.settings import Default
from jsondb.csv2json import Parser
from model.pattern_model import PatternModel

class Table( Check ):
    data = {}

    def __init__(   self, core, name, template):
        self.core = core
        self.model = getattr(core.model, name)
        self.path = core.path
        self.name = name
        self.template = template
        self.keys=[]
        self.lazy = {}
        self.__get_parser__()

        self.html_head = []
        for prop in ('html_head','html_simplefields','html_foreignfields',
        'html_listdictfields', 'html_listfields', 'html_imagefields',
        'html_urlfields','html_foreignlistfields', 'html_dictfields'):
            try: val = self.core.__settings__.get(self.name).get(prop)
            except: val = []
            setattr(self, prop, val)
        
        self.objects = {}
        for i, v in self.model.items():
            self.keys.append(i)
            self.objects[i] = Document(self.core, i, name, self.template, v)

    def __pinit__(self):
        '''
        Post initialization method
        '''
        self.fields=[]
        self.filefields=[]
        self.errors = {}
        
        for k,v in self.objects.items():
            v.__pinit__()            
            if v.errors:
                self.errors[k]= v.errors
        
    def simple_fields(self):
        return [field for field in self.fields if self.__kind__(field) in ('str', 'int', 'float')]

    # TABLE METHODS

    def delete(self):
        '''
        delete template, all documents and current object
        '''
        for i in self.objects.values():
            i.delete()
        os.remove(os.path.join(self.path, 'patterns', '%s.json' % self.name))
        for dir in ('balance', 'html', 'templates'):
            try: os.rmdir(os.path.join(self.path, dir, self.name))
            except: pass
        del self.core.table[ self.name ]
        del self
        return None


    # FIELD METHODS
    def __generate__(self, kind, **kwargs):
        pattern = PatternModel(kind, **kwargs)

        if kind == 'list' or \
        kind == 'dict' and kwargs.get('dynamic'):
            pattern.add(PatternModel(kwargs.get('itemskind') or 'dict'), '$items')

        return pattern.getDict()

    def add(self, target, name, kind='dict', commit=True, **kwargs):
        '''
        Adiing new field into dictionary,
        target dictionaty must be not serial
        '''
        terminate = self.core.__target__(target, name)
        pattern = self.__generate__(kind, **kwargs)
        parent_field = self.__field__(target)
        field = self.__field__(terminate, pattern)

        self.check_add(parent_field, terminate)
        self.check_params(field)
        self.check_value_default(field)
        self.core.check_foreign_key(field.foreign, field.default, terminate)

        self.template = self.__dive__(terminate, pattern).set(self.template)

        if not field.blank:
            for i in self.objects.values():
                i.__recursy_set__(
                    terminate, i.__create__(terminate), commit=commit
                )

        self.save(commit)


    def change(self, target, commit=True, **kwargs):
        '''
        changes options of target, if it allowed
        '''
        pattern = self.structure(target).copy()
        kwargs.update(
            dict([
                (i, kwargs.get(i) if i in kwargs else pattern['$format'].get(i))
                for i in set(kwargs.keys()) | set(pattern['$format'].keys())
            ])
        )        

        kind = self.core.__kind__(pattern['$format'])
        ikind = self.core.__kind__(kwargs)
        update_ = kind != ikind
        if update_:
            kind = kwargs.get('kind')
            kwargs = dict([
                (k,v) for k, v in kwargs.items()
                if k in (u'kind', u'default') or
                (kind == 'dict' and k == 'dynamic')
            ])
            pattern = self.__generate__(**kwargs)

        pattern['$format'] = pattern['$format'].copy()
        pattern['$format'].update(kwargs)
        field = self.__field__(target, pattern)

        self.check_params(field)
        self.check_value_default(field, ignorelength=True)
#        self.core.check_foreign_key(field.foreign, field.default, target)
        self.check_foreign_key(field, self.__items_keys__(target))
        
        if target:
            self.template = self.__dive__(target, pattern).set(self.template)
        else:
            self.template = pattern

        if update_ and not field.blank:
            terminate = '.'.join(target.split('.')[:-1])
            k = self.__kind__(terminate)
            if k not in ('list', 'ddict'):
                terminate = target
            for i in self.objects.values():
                i.set(terminate, i.__create__(terminate), commit=commit)

        self.save(commit)

    
    def exist(self, target):
        '''
        return True if given target exists in tamplate
        '''
        return True if self.structure(target) else False
        

    def remove(self, target, commit=True):
        '''
        moves target value from tamplate, and documents
        return nonthing
        '''
        self.__dive__(target).remove(self.template)
        self.save(commit)

        f = self.__items_keys__(target)

        for i in self.objects.values():
            for t in f:
                if i.exist(t):                    
                    i.__remove__(t, commit)


    def move(self, target, newtarget, commit=True):
        '''
        moves target value to newtaget in tamplate, and documents
        return nonthing
        '''
        value = self.__dive__(target).remove(self.template)
        self.template = self.__dive__(newtarget, value).set(self.template)
        self.save(commit)

        for i in self.objects.values():
            i.__move__(target, newtarget, commit=commit)


    def structure(self,target=''):
        '''
        return subpart of template
        '''
        if not target:
            return self.template
        else:
            return self.__dive__(target).get(self.template)



    # METHOD THAT RETURNS DOCUMENT

    def get(self, id):
        '''
        get document with id is equal to given
        '''
        return self.objects.get(int(id))


    def new(self, commit=True):
        '''
        creates new document from table tamplate
        return document object
        '''
        try:
            key = self.keys[-1] + 1
        except:
            key = 1

        while self.objects.get(key):
            key+=1

        self.objects[key] = Document(self.core, key, self.name, self.template,
            None, new=True).__clean__(commit)
        self.objects[key].__pinit__()
        
        return self.objects[key]


   # METHOD THAT RETURNS QUERYSET

    def filter(self, target, value, **kwargs):
        '''
        return queryset object, contains documents,
        which target value is equal to given value
        '''
        return QuerySet(self, self.objects.values()).filter(target, value)


    def exclude(self, target, value, **kwargs):
        '''
        return queryset object, contains documents,
        which target value is NOT equal to given value
        '''
        return QuerySet(self, self.objects.values()).exclude(target, value)


    def order_by(self, target):
        '''
        return queryset object, contains documents,
        ordered by given value

        if you want give reverse sorded list, just type "-target"
        '''
        return QuerySet(self, self.objects.values()).order_by(target)


    def all(self):
        '''
        return queryset object, contains all documents
        '''
        return QuerySet(self, self.objects.values())

    # EXPORT & IMPORT METHODS TO DIFFERENT FORAMT

    def dumps(self, file, fields=None):
        """
        Export data in file
        """
        parser = self.parser(file, table = self.name, api = self.core.api,
            index = 0, ignored=[], delimiter=';')
        parser.export(fields)

    def loads(self, file, sync=False):
        """
        Import data from file
        """
        parser = self.parser(file, self.name, api=self.core.api, delimiter=";")
        parser.execute()
        if sync: parser.sync()

    def html(self, objects=None, per_page=10000):
        if objects: acontext= [i.view.data for i in objects]
        else: acontext= [i.view.data for i in self.objects.values()]
        tables = self.core.table
        pagename = self.name

        p = Paginator(acontext, per_page)
        for page in p.page_range:
            context = p.page(page).object_list
            if page != 1: filename = 'index%s.html' % page
            else: filename = 'index.html'

            file = open(os.path.join(self.core.path, 'html', self.name, filename), 'w+')
            content = render_to_response(os.path.join(self.name, 'index.html'), locals()).content
            file.write(content)
            file.close()
        for i in self.objects.values():
            i.html()

    def __amf__(self):
        fields = [i for i in self.fields if self.__field__(i).compressed]
        return dict([(str(k), v.__amf__(fields)) for k, v in self.objects.items()])

    # SAVE

    def save(self, commit=True):
        '''
        save the corrent document to hard drive,
        it autoatically calls when document or table pattern has changed
        '''
        self.core.changed.append(self)
        if commit:
            file = codecs.open(
                os.path.join( self.path, 'patterns', '%s.json' % self.name),
                'w+', Default.encoding
            )
            file.write(self.core.encoder(self.template))
            file.close()

        return self

    def sync(self):
        self.save()

        for i in self.objects.values():
            i.save()


    # PRIVATE
    
    def __dive__(self, target, value=''):
        '''
        private method, to convinient work with dictionaries
        '''
        return Dive(target, self.template, value, self)

    def __kind__(self, target):
        '''
        Get internal kind if existing item
        do not use during add or create items
        '''
        return self.core.__kind__(self.structure(target)['$format'])

    def __field__(self, target, data=None):
        if data is None:
            data = self.structure(target)
        try:
            return Field(self.core, data, target)
        except:
            raise KeyError("%s does't Exist" % target)

    def __data__(self):
        return dict([(k, v.data) for k, v in self.objects.items()])


    # SETTINGS

    def __get_settings__(self, name):
        try:
            return self.core.__settings__[self.name][name]
        except:
            return ''

    def __get_parser_name__(self):
        return self.__get_settings__('parser')

    def __get_parser__(self):
        name = self.__get_parser_name__()
        if name:
            exec "from %s import MyParser" % name
            self.parser = MyParser
        else:
            self.parser = Parser

    def __set_settings__(self, key, value):
        if self.name not in self.core.__settings__:
            self.core.__settings__[self.name] = {}
        self.core.__settings__[self.name][key] = value

    def __set_parser__(self, name):
        self.__set_settings__('parser', name)
        self.core.__set_settings__()

    def __set_fast_fields__(self, fields):
        self.__set_settings__('fast_fields', fields)
        self.core.__set_settings__()

    def __items_keys__(self, target):
        f = [target]
        if "$items" in target.split('.'):
            t = target.replace("$items", '[A-Za-z0-9]')
            f = [trg for trg in self.fields if re.match(t, trg)]
        return f