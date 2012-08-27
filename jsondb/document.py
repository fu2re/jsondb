import re
# coding: utf-8
import os
import codecs
import string
import copy
import urllib
import time

#from django.shortcuts import render_to_response
from utils.settings import Default
from utils.dive import Dive
from jsondb.csv2json import Parser
from field import Field

class Document(object):
    data = {}
    defaults = {
        'dict': {},
        'ddict': {},
        'list': [],
        'int': 0,
        'float': 0.0,
        'str': '',
        'unicode': u''
    }

    def __init__(self, core, id, section, template, model, new=False):
        self.core = core
        self.__item__ = model        
        self.path = core.path
        self.id = id
        self.table = section
        self.template = template
        self.initializated = False
        self.lazy = {}
        self.__ft__ = {}

        if not new:
            self.__assotiate__()

    def __pinit__(self):
        """
        Post initialization procedure
        """
        self.fields = []
        self.filefields = []
        self.errors = []
        self.valid = self.validate()
        self.__targets__()
        self.initializated = True
        


    # DOCUMENT METHODS

    def delete(self):
        """
        Remove entire document
        """
        foreigns = self.core.assotiates(
            self.table,
            'in',
            str(self.view.id)
        )
        if foreigns:
            count = 0
            for v in foreigns.values():
                count += len(v)
            raise ValueError(
                """
                Cant delete document because other documents
                refers to it (%s), for detail report call
                JsonDBinstanse.assotiates('%s','in','%s')
                """ % (count, self.table, self.view.id)
            )
            
        self.__assotiate_clean__()
        
        del self.t.objects[self.id]
        try:
            os.remove(os.path.join(self.path, 'balance', self.table,
                '%s.json' % self.id))
        except:
            pass
        del self.__item__
        del self
        return None


    def save(self):
        '''
        Public save method
        '''
        self.__save__(self.data, commit=True)


    @property
    def view(self):
        '''
        return staticModel of current document
        '''
        return self.__item__


    # DOCUMENT FIELD METHODS

    def get(self, target=''):
        '''
        return value of target field
        '''
        if not target:
            return self.data
        else:
            if target in self.lazy:
                return self.lazy[target]
            data = self.__dive__(target).get(self.data)
            self.lazy[target] = data
            return data

    def get_related(self, target):
        return self.core.table[self.__field__(target).foreign].get(self.get(target))

    def set(self, target, value=None, commit=True):
        '''
        set value of target field to giben value
        return nonthing
        '''
        if not target:
            raise KeyError("You can't set entire document")
        field = self.__field__(target)
        if field.kind in ('dict', 'ddict', 'list'):
            if value is None:
                value = self.__create__(target)
            elif not self.validate(target, value):
                raise ValueError("Data is't valid, %s" % target)
        else:
            self.core.check_foreign_key(field.foreign, value, target)
            self.t.check_value_default(field, value)
        data = self.__dive__(target, value).set(self.data)        
        self.__clear_lazy__(target)
        data = self.__save__(data, commit)
        if field.foreign:
            self.__assotiate_clean__()
            self.__assotiate__()
        self.__fields__(target, field)
        return data

    def __recursy_set__(self, target, value=None, commit=True):
        t = target.split('.')
        if '$items' in t:
            pos = t.index('$items')
            target = '.'.join(t[:pos])
            v = self.get(target)
            if not target:
                del v['id']
            keys = xrange(len(v)) if self.__field__(target).kind == 'list' else v.keys()
            
            for i in keys:
                self.__recursy_set__('.'.join(t[:pos] + [str(i)] + t[pos+1:]), value, commit=False)
        else:
            self.set(target, value, commit)


    def exist(self, target):
        '''
        return true if target field of document is exist,
        otherwise, it returns none

        it make sence use this method only for dynamic dictionary, or list
        '''
        return not self.get(target) is None

    def retrieve(self, target, local_file=None):
        """
        Return binary data of remote file of file field
        if local_file atribute is not specified,
        else save data into this file
        """
        url = self.get(target)
        field = self.__field__(target)
        if not url or not field.is_file:
            raise ValueError('field is not have url')

        if local_file:
            return urllib.urlretrieve(url, local_file)
        else:
            return urllib.urlopen(url).read()


    def validate(self, target='', data=None):
        """
        Returns True if data is according to pattern
        """
        field = self.__field__(target)
        target = string.replace(target, '$items', '0')
        if data is None: data = self.get(target)

        valid = []        
        if field.is_file:
            return True

        if (field.kind == 'str' and type(data) not in (unicode, str)) and \
        type(data) != type(self.defaults[ field.kind ]):
            self.__error__(target)
            return False

        if field.kind in ('int', 'float', 'str'):
            try:
                self.t.check_value_default(field, data)
            except:
                self.__error__(target)
                return False

        elif field.kind in ('list', 'ddict'):
            try:
                self.t.check_value_length(field, data)
            except:
                self.__error__(target)
                return False

            for key, value in enumerate(data) if field.kind == 'list' else data.items():
                if key in ('id',):
                    continue
                if not self.validate(self.core.__target__(target, key), value):
                    valid.append(False)

        elif field.kind == 'dict':
            
            for key, val in data.items():
                if key in ('id',):
                    continue

                if not field.pattern.get(key):
                    self.__error__(self.core.__target__(target, key))
                    return False
                
#                valid = self.validate( self.core.__target__(target, key), val )
            
            for key, val in field.pattern.items():
                if key in ('$format',) or val['$format'].get('blank'):
                    continue

                if key not in data:
                    self.__error__(self.core.__target__(target,key))
                    return False

                if not self.validate(self.core.__target__(target, key)):
                    valid.append(False)
            
        return False if False in valid else True


    # DOCUMENT FIELD METHODS, THAT CAN ONLY BE APPLYED TO LIST FIELD,
    # OR DYNAMIC DICTIONARY(NAMED LIST)

    def __check_add__(self, target, value=False, key=None):
        parent = self.get(target)
        field=self.__field__(target)

        if field.kind not in ('ddict', 'list'):
            raise KeyError("Adding not allowed, %s is not list or dynamic dict, use set insted" % target)

        self.t.check_max(self.__field__(parent.target), parent)
        self.core.check_foreign_key(field.items.foreign, value, target)
        if value: 
            self.t.check_value_default(
                self.__field__(self.core.__target__(target, key)), value,
                ignoredefault=True
            )

    def add(self, target, value=False, key=None, commit=True):
        '''
        add new element in list or ddict
        '''
        field=self.__field__(target)
        
        if field.kind == 'list': key = len(self.get(target))
        if field.kind == 'ddict' and not key:
            key = 1
            while self.exist(self.core.__target__(target, key)):
                key += 1

        if not value:
            value = self.__create__(self.core.__target__(target, key))
        self.__check_add__(target, value, key)

       # if not self.validate(target = '%s.$items' % target, data = value):
         #   value = self.__create__(target, parent)

        terminate = self.core.__target__(target, key)
        data = self.__dive__(terminate, value = value).set(self.data)
        self.__clear_lazy__(terminate)

        data = self.__save__(data, commit)
        self.__assotiate_clean__()
        self.__assotiate__()
        self.__fields__(terminate, field.items)
        return data

    def switch(self, target, index, terminate, commit=True):
        """
        Switch two elements in list:
        A, B = B, A
        """
        field = self.__field__(target)
        if not field.kind == 'list':
            raise TypeError('Object is not list, %s' % target)

        value = self.get(target)
        item = value.pop(index)
        value.insert(terminate, item)

        data = self.__dive__(target, value).set(self.data)
        self.__clear_lazy__(target)

        data = self.__save__(data, commit)
#        self.save()


    def remove(self, target, commit=True):
        if not target:
            raise KeyError("Can't remove entire document, use delete method instead")

        parent_field = self.__field__('.'.join(string.split(target, '.')[:-1]))
        field = self.__field__(target)

        if not (parent_field.kind in ('list', 'ddict') or field.blank):
            raise KeyError("Field can't be deleted, %s" % target)

        self.t.check_min(parent_field, self.get(parent_field.target), True)            
        return self.__remove__(target, commit=commit)

    # EXPORT & IMPORT METHODS TO DIFFERENT FORAMT

    def dumps(self, file, target, fields=None):
        parser = Parser(
            file,
            table = self.table,
            api = self.core.api,
            index = 0,
            ignored=[1],
            delimiter=';'
        )
        parser.export_once(target, self, fields)

    def loads(self, file, name=0):
        parser = Parser(file, table = self.table, api = self.core.api,
            index = 0, ignored=[1], delimiter=';')
        parser.once(document=self, name_col=name)

    def html(self):
        context = self
        tables = self.core.table
        file = open(os.path.join(self.core.path, 'html', self.table, '%s.html' % self.__item__.id), 'w+')
        content = render_to_response(os.path.join(self.table, 'doc.html'), locals()).content

        file.write(content)
        file.close()

    @property
    def t(self):
        return self.core.table[self.table]

    @property
    def data(self):
        return self.__item__.data

    @property
    def helptext(self):
        fields = self.t.__get_settings__('fast_fields')
        return '\n'.join([
            '%s: %s'% (self.__field__(i).text or i, self.get(i) or '')
            for i in fields
        ])

    # PRIVATE
    def __targets__(self, target='', data=None):
        if target == 'id': return
        field = self.__field__(target)
        self.__fields__(target, field)
        if field.kind in ('list', 'dict', 'ddict'):
            if not data: data = self.get(target)
            keys = enumerate(data) if field.kind == 'list' else data.items()            
            for k, v in keys:
                self.__targets__(self.core.__target__(target, k), v)


    def __fields__(self, target, pattern):
        if target not in self.fields:
            self.fields.append(target)

        if target not in self.t.fields:
            self.t.fields.append(target)

        if pattern.is_file:
            if target not in self.filefields:
                self.filefields.append(target)

            if target not in self.t.filefields:
                self.t.filefields.append(target)


    def __filter__(self, target, value):
        '''
        return self if value of target field is equal to given value
        otherwise, it returns none
        '''
        try:
            value = value.decode('utf-8')
        except:
            pass        
        return self if self.get(target) == value else None
        
    def __exist__(self):
        '''
        return True if document exist,
        otherwise, it returns none
        '''
        return True if self.__item__ else False


    def __move__(self, target, newtarget, commit=True):
        '''
        move the target data, to new destionation
        it automatically calls when moves data in tamplate
        '''
        try:
            value = self.__dive__(target).remove(self.data)
            data = self.__dive__(newtarget, value).set(self.data)
            self.__save__(data, commit)
        except:
            field=self.__field__(newtarget)
            if not field.blank:
                raise KeyError('No such key %s' % target)



    def __save__(self, data, commit):
        '''
        save the corrent document to hard drive,
        it autoatically calls when document or table pattern has changed
        '''
        self.core.changed.append(self)
        if commit:
            file = codecs.open(os.path.join(self.path, 'balance', self.table,
                '%s.json' % self.id), 'w+', Default.encoding)            
            cdata = copy.copy(data)
            try: del cdata['id']
            except: pass
            file.write(self.core.encoder(cdata))            
            file.close()
        self.__item__ = self.core.loader.load_from_data(self.table, data, self.id)
        return self


    def __remove__(self, target, commit=True):
        '''
        removes Data from target field
        calls only from table
        '''
        self.__assotiate_clean__()
        data = self.__dive__(target).remove(self.data)
        self.__clear_lazy__(target)
        self.__save__(self.data, commit)
#        self.__assotiate_clean__()
        self.__assotiate__()
        return data

    def __dive__(self, target, value=''):
        '''
        private method, to convinient work with dictionaries
        '''
        return Dive(target, self.template, value, self)

    def __clean__(self, commit=True):
        '''
        generate entire new model from tamplate
        '''
        return self.__save__(self.__create__(''), commit)

    def __create__(self, target,  **kwargs):
        '''
        generate new field from template
        '''
        field = self.__field__(target)
        if field.kind == 'list':
            data = [
                self.__create__(self.core.__target__(target, '$items'))
                for i in xrange(field.min or 0)
            ]
        
        elif field.kind == 'dict':
            data = dict([
                (k, self.__create__(self.core.__target__(target, k)))
                for k, v in field.keys.items()
                if not v['$format'].get('blank')
            ])

        elif field.kind == 'ddict':
            if field.foreign:
                xr = self.core.table[field.foreign].keys()[:field.min]
            else:
                xr = xrange(field.min or 0)

            data = dict([
                (k, self.__create__(self.core.__target__(target, '$items')))
                for k in xr
            ])

        elif  field.kind == 'int' and field.foreign and not field.default:
            data = self.core.table[field.foreign].objects[0].id

        else:
            if field.default is not None:
                data = field.default
            else:
                data = copy.copy(self.defaults[field.kind])                
        return data


    def __assotiate_clean__(self):
        try:
            for i,v in self.core.foreigns[self.table]['out'][str(self.view.id)].items():
                for ii in v:
                    self.core.foreigns[i]['in'][ii][self.table].remove(str(self.view.id))
            del self.core.foreigns[self.table]['out'][str(self.view.id)]
        except:
            pass


    def __assotiate__(self, data=None, target=''):
        keys = []
        def __assotiate_int__(self, field, data):
            self.core.__assotiate_append__(self.table, 'out', str(self.view.id),
                field.foreign, str(data))
            self.core.__assotiate_append__(field.foreign, 'in', str(data),
                self.table, str(self.view.id))

        root_level = False
        field = self.__field__(target)
        if not target:
            data = self.data
            root_level = True
        
#        if not data:
#            return
#        elif target:
#            if field.kind not in ('ddict', 'list'):
#                return

        if field.kind in ('dict', 'ddict'):
            keys = data.keys()
        elif field.kind == 'list':
            keys = [str(i[0]) for i in enumerate(data)]
        
        terminate = target
        idata=data
        for i in keys:
            if root_level and i == 'id':
                continue
            target = self.core.__target__(terminate, i)
            field = self.__field__(target)
            data = self.__dive__(i).get(idata)
            if field.foreign:
                if field.kind == 'ddict':
                    for key in data.keys():
                        self.core.__assotiate_append__(field.foreign, 'in',
                            key, self.table, str(self.view.id))
                    self.core.__assotiate_extend__(self.table, 'out',
                        str(self.view.id), field.foreign,data.keys())
                elif field.kind == 'int':
                    __assotiate_int__(self, field, data)                    
            self.__assotiate__(data, target)

    def __error__(self, field):
        if not self.initializated:
            self.errors.append(field)
            
    def __field__(self, target):
        if target in self.__ft__:
            return self.__ft__[target]
        
        if not target:
            t = self.template
        else:
            t = self.__dive__(target).get(self.template)
        try:
            field = Field(self.core, t, target)
            self.__ft__[target] = field
            field.format
        except:
            raise KeyError("Template error: %s, field %s does't exist" % (self.table, target))
        return field

    def __amf__(self, fields):
        copyed = copy.copy(self.data)
        if 'id' in copyed: del copyed['id']
        deleted = list(set(self.fields) - set(fields))
        for target in deleted:
            if target != '':
                self.__dive__(target).remove(copyed)
        return copyed

    def __clear_lazy__(self, target):
        for key in self.lazy.keys():
            if key.startswith(target):
                del self.lazy[key]