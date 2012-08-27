# coding: utf-8
# Модуль создания, редактирования файла со списком проектов
import copy
import traceback
import sys
from jsondb import JsonDB


class Project(object):
    """Хранилище данных о проекте"""

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self._load()

    def _load(self):
        try:
            self.data = JsonDB(self.path, project_name=self.name)
            self.error = None
        except:
            self.data = None
            self.error = traceback.format_exc()
            #str(sys.exc_info()[1])

class ProjectsManager(object):
    """Для чтения и записи даных о всех добавленных проектах"""

    pattern = {
        'str':{
            'kind':True,
            'default':True,
            'text':False,
            'blank':False,
            'min':False,
            'max':False,
            'values':False,
            'is_file':False
        },
        'int':{
            'kind':True,
            'default':True,
            'text':False,
            'blank':False,
            'min':False,
            'max':False,
            'values':False,
            'foreign_key':False,
            'nocompress':False
        },
        'float':{
            'kind':True,
            'default':True,
            'text':False,
            'blank':False,
            'min':False,
            'max':False,
            'values':False,
            'nocompress':False
        },        
        'dict':{
            'kind':True,
#            'dynamic':False,
            'text':False,
            'blank':False,
            'nocompress':False
        },
        'list':{
            'kind':True,
            'text':False,
            'blank':False,
            'min':False,
            'max':False,
            'nocompress':False
        },
        'dynamic dict':{
            'kind':True,
#            'dynamic':False,
            'text':False,
            'blank':False,
            'min':False,
            'max':False,
            'foreign_key':False,
            'nocompress':False
        }
    }
    converter = {
        'int':int,
        'float':float,
        'str':unicode
    }
    
    def __init__(self):
        self.__projects = []
        self.__dctProjects = {}  # project.name -> project

    def update(self, key, remote):
        for project in self.projects:
            try:
                project.data.private_key = '%s' % key
                if remote:
                    project.data.core.remote_static_server = '%s' % remote
            except:
                pass

    @property
    def projects(self):
        """Возвращает все определенные проекты"""
        return self.__projects

    def getProjectByName(self, name):
        """Возвращает проект по наименованию name, или None"""
        return self.__dctProjects.get(name)

    def addProject(self, name, path):
        """Добавляет новый проект и записывает его в файл"""
        #self.__projects.append({'name': name, 'path': path})
        project = Project(name, path)
        self.__projects.append(project)
        self.__dctProjects[name] = project
        self.save()

    def delProject(self, name):
        """Удаляем проект по имени name"""
        project = self.__dctProjects.get(name)        
        if project is not None:
            self.__projects.remove(project)
            del self.__dctProjects[name]
            self.save()

    def renameProject(self, name, newname):
        """Удаляем проект по имени name"""
        project = self.__dctProjects.get(name)
        if project is not None:
            project.name = newname
            self.__dctProjects[newname] = project
            del self.__dctProjects[name]
            self.save()

    def load(self, fileName='projects.ini'):
        """Читает данные о проектах из файла fileName"""
        try:
            file = open(fileName)
            for record in file.readlines():
                if record.replace('\n', '') != '':
                    try:
                        projectDct = eval(record)
                    except NameError:
                        continue
                    name, path = projectDct.get('name', ''), projectDct.get('path', '')
                    if len(name) > 0 and len(path) > 0:
                        project = Project(name, path)
                        self.__projects.append(project)
                        self.__dctProjects[name] = project
            file.close()
        except IOError:
            self.__projects = []

    def save(self, fileName='projects.ini'):
        """Сохраняет проекты в файл fileName"""
        try:
            file = open(fileName, 'w')
            file.writelines(
                [u'%s\n' % {'name': p.name, 'path': p.path} for p in self.__projects])
            file.close()
        except IOError:
            self.__projects = []


projectManager = ProjectsManager()
projectManager.load()
projectManager.save()
#print projectManager.projects
