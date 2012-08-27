# coding: utf-8
import csv
import string
import json
import codecs

from jsondb import *
from utils.settings import Default

def OpenOfficeIndex(index):
    keys = dict([(k,v)for k,v in enumerate(list('ABCDEFGHIJKLMNOPQRSTUWXYZ'))])
    key = keys.get(index)
    if key: return key
    else: return '%s%s' % (keys[index/25-1], keys[index%25-1])

class Message(object):
    warnings=[]
    panic = False

    def warning(self, text):
        self.warnings.append(text)

    def error(self, text):
        self.panic = True
        self.warnings.append(text)


class Parser(object):
    def __init__(self, path_csv, table, path=None, api=None, ignored=None,
            index=None, delimiter=Default.delimiter, quotechar=Default.quotechar):

        if not path and not api:
            raise Exception('wrong init parameter')

        self.delimiter = delimiter
        self.path_csv = path_csv
        try:
            self.csv = csv.reader(
                open(path_csv, 'rb'),
                delimiter=self.delimiter,
                quotechar=quotechar
            )
        except:
            pass

        self.ignored_index = []
        self.msg = Message()
        self.proceeded = []

        if ignored is None:
            ignored = Default.string_ignored
        self.ignored_index.extend(ignored)

        if index is None:
            index = Default.string_index
        self.index_index = index

        self.api = api or JsonDB(path)
        self.table = table

    # JsonDB -> csv

    def export(self, fields=None):        
        """
        Экспорт таблицы в файл
        """
        if not fields:
            fields = sorted([field for field in self.t.fields
                if self.t.structure(field)['$format']['kind'] not in ('dict', 'list')
            ])
        elif type(fields) is not list:
            raise TypeError('Wrong type of fields: %s instead list' % type(fields))
        texts = ['']
        self.types = {}
        for i in fields:
            try:
                self.types[i] = self.t.structure(str(i))['$format']['kind']
                texts.append((self.t.structure(str(i))['$format'].get('text') or '').encode('utf-8'))
            except:
                raise KeyError("Document havn't %s field" % i)

        file = open(self.path_csv, 'w+')
        ex = ['id']
        ex.extend(fields)
        file.write('%s\n' % self.delimiter.join(ex))
        file.write('%s\n' % self.delimiter.join(texts))

        for id, doc in self.t.objects.items():
            ex = [str(id)]
            for field in fields:
                v = doc.get(field)
                ex.append(self.__define_type__(v, field))
            file.write('%s\n' % self.delimiter.join(ex))
            
        file.close()


    # csv -> JsonDB

    def execute(self):
        """
        Экспорт из csv файла в таблицу
        """
        for row in self.csv:            
            if self.csv.line_num == self.index_index:
                self.init_index(row)

            elif self.csv.line_num not in self.ignored_index:
                self.parse_row(row)

        for document in self.proceeded:
            document.save()
            
        return self.msg.warnings

    def sync(self):
        """
        Удаляет документы которых нет в таблице
        """
        for iter, row in enumerate(self.csv):
            if iter == self.index_index:
                self.init_index(row)
                break
                
        old = [i for i in self.t.objects.values()]
        new = [int(i[self.id]) for i in self.csv]
        for doc in old:
            if doc.view.id not in new:
               doc.delete()


    # PRIVATE

    def parse_row(self, row):
        """
        парсинг ячейки csv таблицы
        """
        id = row[self.id]

        if id == u'new':
            document = self.t.new(commit=False)
        else:
            document = self.t.get(id)

        for iter, value in enumerate(row):
            if iter != self.id and value != '':                
                try:
                    value = self.__define_type_set__(value, self.index[iter], self.csv.line_num, iter)
                    document.set(self.index[iter], value, commit=False)
                except:
                    raise TypeError(
                        "Line %s, col %s(%s): Wrong Type of Value" % \
                        (self.csv.line_num, iter+1, OpenOfficeIndex(iter))
                    )
                self.proceeded.append(document)


    def init_index(self, row):
        """
        Определяет индекс стобца ID, и запоминает типы требуемых полей
        """
        self.types = {}
        self.index = row
        for i,value in enumerate(self.index):
            v = value.strip()
            if v == 'id':
                self.id = i
            else:
                try:
                    self.types[value] = self.t.structure(v)['$format']['kind']
                except:
                    raise KeyError("Line %s, col %s(%s): Wrong target" % \
                        (self.csv.line_num,i+1, OpenOfficeIndex(i)))

    @property
    def t(self):
        """
        Возвращает объект jsondb.table
        """
        return self.api.table[self.table]

    def __define_type__(self, v, field):
        """
        Конвертер при экспорте
        """
        if v is None: return ''
        elif self.types[field] == 'str': return v.encode('utf-8')
        elif self.types[field] in ('int', 'float'): return str(v)
        else: return json.dumps(v, ensure_ascii=False, encoding='utf-8').encode('utf-8')


    def __define_type_set__(self, v, field, row, col):
        """
        Конвертер при импорте
        """
        if self.types[field] == 'float': return float(v)
        elif self.types[field] == 'int': return int(v)
        elif self.types[field] in ('dict', 'list'):
            try:
                return json.loads(v)
            except:
                raise ValueError(
                    "Line %s, col %s(%s): No JSON object could be decoded" % \
                    (row, col+1, OpenOfficeIndex(col))
                )
        else: return v.decode('utf-8')


    # DEPRECATED

    def once(self, document=None, id=None, name_col=0):
        """
        Экспорт из csv файла в документ
        """
        if not document and not id:
            raise Exception('Wrong Arguments')

        self.name_col = name_col

        if not document:
            if id == u'new':
                document = self.t.new()
            else:
                document = self.t.get(id)

        for iter, row in enumerate(self.csv):
            if self.csv.line_num == self.index_index:
                self.init_index([
                    document.core.__target__(row[0], '$items', i) \
                    for k,i in enumerate(row) \
                    if k != 0
                ])

            elif self.csv.line_num not in self.ignored_index:
                document = self.parse_once(row, document)

            if self.msg.panic:
                break

        document.save()
        return self.msg.warnings

    def parse_once(self, row, document):
        """
        парсинг ячейки csv документа
        """
        name = row[ self.name_col ]
        for iter, value in enumerate(row):
            if iter != self.name_col and value != '':
                target = string.replace(self.index[iter-1],'$items', name, 1)
                value = self.__define_type_set__(value, self.index[iter-1], self.csv.line_num, iter)
                document.set(target, value, commit=False)

        return document

    def export_once(self, target, document, fields):
        """
        Экспорт документа в отдельную таблицу
        не поддерживается текущей версией JsonDB Explorer
        """
        data = document.get(target)
        kind = self.t.structure(target)['$format']['kind']
        dynamic = self.t.structure(target)['$format'].get('dynamic')

        if kind == 'list': keys = [k for k,v in enumerate(data)]
        elif kind =='dict' and dynamic: keys = data.keys()
        else:
            raise KeyError('Target %s is not iterable' % target)

        if not fields:
            fields = ['']

        elif type(fields) is not list:
            raise TypeError('Wrong type of fields: %s instead list' % type(fields))

        ex = [target]
        texts = [self.t.structure(target)['$format'].get('text') or '']
        self.types = {}
        for i in fields:
            try:
                tp = self.t.structure(
                    document.core.__target__(target,'$items', i)
                )['$format']
                self.types[i] = tp['kind']
                texts.append(tp.get('text') or '')

            except:
                raise KeyError("Document havn't %s field" % i)

        ex.extend(fields)

        file = open(self.path_csv, 'w+')
        file.write('%s\n' % self.delimiter.join(ex))
        file.write('%s\n' % self.delimiter.join(texts))

        for id in keys:
            ex = [str(id)]
            for field in fields:
                v = document.get(document.core.__target__(target, id, field))
                ex.append(self.__define_type__(v, field))
            file.write('%s\n' % self.delimiter.join(ex))

        file.close()