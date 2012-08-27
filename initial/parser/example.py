# coding: utf-8
from jsondb.csv2json import Parser

class MyParser(Parser):
    def __init__(self, path_csv, table, api=None, ignored=None,
        index=None, delimiter=None, quotechar=None):
        """
        Параметры:
        >>> path_csv # путь в которых сохранять файл, завпись в файл должны быть произведена в скрипте
        >>> api # Объект класса jsonDB
        >>> table # Имя таблицы
        >>> ignored # Игнорируемые строки в csv
        >>> index # Индексная строка в csv файле (строка с адресами)
        >>> delimited # Разделитель полей в csv (по умолчанию ;)
        >>> quotechar # Символ цитирования в csv (по умолчанию \)

        Унаследованные методы и свойства:
        JsonDB -> csv
        >>> export(fields) # Экспорт таблицы в файл
        >>> export_once(target, document, fields) # Экспорт документа в отдельную таблицу

        csv -> JsonDB
        >>> execute() # Экспорт из csv файла в таблицу
        >>> sync() # Удаляет документы которых нет в таблице
        >>> once(document, id, name_col) # Экспорт из csv файла в документ

        PRIVATE
        >>> self.t # объект jsondb.table
        >>> init_index() # Определяет индекс стобца ID, и запоминает типы требуемых полей
        >>> parse_row(row) # парсинг ячейки csv таблицы
        >>> parse_once(row, document) # парсинг ячейки csv документа
        >>> self.__define_type__(v, field) # Конвертер при экспорте
        >>> self.__define_type_set__(v, field) # Конвертер при импорте

        Usage:
        ознакомиться с исходниками, заменить необходимые методы
        """
        Parser.__init__(
            self, path_csv, table, api=api, ignored=ignored,
            index=index, delimiter=delimiter, quotechar=quotechar
        )
        
    def init_index(self):
        print "Yep, I'm Here"

    def execute(self):
        print "Yep, I'm Here"