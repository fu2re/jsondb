# coding: utf8
#
# version 0.4
# by fu2re
#
import os
import sys
import json
import codecs
import pyamf
import string
#os.environ['DJANGO_SETTINGS_MODULE'] = "jsondb.utils.dj_settings"

#from django.conf import settings
from table import Table
from utils.settings import Default
from checks import CoreCheck
from mercurial import ui, hg, commands
from utils.StaticLoader import StaticLoader
from model.pattern_model import PatternModel
from jsondb.utils.upload import upload_file

props = (
    'html_head','html_simplefields','html_foreignfields','html_listdictfields',
    'html_listfields', 'html_imagefields', 'html_urlfields',
    'html_foreignlistfields', 'html_dictfields'
)

class Model( object ):
    pass


class Core( CoreCheck ):
    changed = []
    defaults = {
        'int':0,
        'str':'',
        'float':0.0,
    }
    def __init__(cls, path, remote_static_server=None, api=False):
        path = os.path.abspath(path)
        cls.model = Model
        cls.load_content(path)
        cls.api = api
        cls.table = {}
        cls.foreigns = {}
        cls.path = path
        cls.encoder = json.JSONEncoder(ensure_ascii=False, sort_keys=True, indent=4).encode
        cls.decoder = json.JSONDecoder(Default.encoding).decode
        cls.remote_static_server = remote_static_server or Default.remote_static_server
        cls.errors = {}
        cls.__get_settings__()
        files = [i for i in os.listdir(os.path.join(path,'patterns')) if i.endswith('.json')]

        for i in files:
            if i == '__settings__.json': continue
            file = codecs.open(os.path.join(path,'patterns',i), 'r', Default.encoding)
            data = cls.decoder(file.read())
            file.close()

            name = string.split(i,'.')[-2]
            cls.table[ name ] = Table(
                core = cls,
                name = name,
                template = data
            )
            cls.table[ name ].__pinit__()
            if cls.table[ name ].errors:
                cls.errors[name] = cls.table[ name ].errors
#        settings.TEMPLATE_DIRS.append(os.path.join(path, 'templates'))
#        settings.STATIC_URL = cls.remote_static_server

    def load_content(cls, path):
        cls.loader = StaticLoader(path)
        for name in cls.loader.collections():
            setattr(cls.model, name, cls.loader.models(name))


    def __assotiate_create__(cls, i1, i2, i3, i4):
        if not cls.foreigns.get( i1 ):
            cls.foreigns[ i1 ] = {'in':{},'out':{}}
        if not cls.foreigns[ i1 ][ i2 ].get( i3 ):
            cls.foreigns[ i1 ][ i2 ][ i3 ] = {}
        if not cls.foreigns[ i1 ][ i2 ][ i3 ].get( i4 ):
            cls.foreigns[ i1 ][ i2 ][ i3 ][ i4 ] = []

    def __set_settings__(cls, val=None):
        if not val:
            val = cls.__settings__
        try:
            file = codecs.open(os.path.join(cls.path,'patterns','__settings__.json'), 'w', Default.encoding)
            file.write(cls.encoder(val))
            cls.__settings__ = val
            file.close()
        except:
            pass

    def __get_settings__(cls):
        try:
            file = codecs.open(os.path.join(cls.path,'patterns','__settings__.json'), 'r', Default.encoding)
            cls.__settings__ = cls.decoder(file.read())
            file.close()
        except:
            pass

    def __assotiate_append__(cls, i1, i2, i3, i4, value):
        cls.__assotiate_create__(i1, i2, i3, i4)
        cls.foreigns[ i1 ][ i2 ][ i3 ][ i4 ].append( value )


    def __assotiate_extend__(cls, i1, i2, i3, i4, value):
        cls.__assotiate_create__(i1, i2, i3, i4)
        cls.foreigns[ i1 ][ i2 ][ i3 ][ i4 ].extend( value )

    def create(cls, name, dynamic=0, **kwargs):
        file = codecs.open(
            os.path.join(
                cls.path, 'patterns', '%s.json' % name
            ), 'w+', Default.encoding
        )

        pattern = PatternModel(dynamic=dynamic)
        if dynamic:
            pattern.add(
                PatternModel(kwargs.get('itemskind') or 'dict'), '$items'
            )

        file.write(cls.encoder(pattern.getDict()))
        file.close()
        for dir in ('balance',):
            os.mkdir(
                os.path.join(cls.path, dir, name)
            )
        cls.model = Model
        cls.load_content(cls.path)
        cls.table[ name ] = Table(
            core=cls, name=name, template=pattern.getDict()
        )
        cls.table[ name ].__pinit__()


    def save(cls):
        file = open(os.path.join(cls.path, 'patterns', '__settings__.json'), 'w+')
        sett = {}
        for k,v in cls.table.items():
            sett[k] = {}
            for prop in props:
                sett[k][prop] = getattr(v,prop) or []

        file.write(cls.encoder(sett))
        file.close()

    def assotiates(cls, *args):
        data = cls.foreigns
        for i in args:
            data = data.get( i )
            if not data:
                return None
        return data

    def __kind__(self, kwargs):
        if kwargs.get('dynamic'):
            return 'ddict'
        return kwargs.get('kind')
    
    def __target__(self, *args):
        return '.'.join([str(i) for i in args if str(i)])

class Message(object):
    warnings=[]
    panic = False

    def warning(self, text):
        self.warnings.append(text)

    def error(self, text):
        self.panic = True
        self.text = text
        self.warnings.append(text)
        return self


class JsonDB(object):
    def __init__(self, path, remote_static_server=None, debug=False, project_name=None):
        self.debug=debug
        try:
            sys.path.append(os.path.join(path, 'parser'))
        except:
            pass
        self.core = Core(path, remote_static_server, self)
        self.core.wrapper = self
        self.errors = self.core.errors
        self.table = self.core.table
        self.path = path
        self.project_name = project_name or os.path.split(path)[1]
        self.private_key = None
        


    def create(self, name, dynamic=0):
        self.core.create(name, dynamic)

    def amf(self, tables, path=None, upload=False, tags='', summary=None):
        amf = pyamf.encode(
            dict([(t, self.table[t].__amf__()) for t in tables])
        ).read()
        temp = path or 'balance_%s_%s.amf' % self.summary()
        f = open(temp, 'wb')
        f.write(amf)
        f.close()
        if upload:
            a = self.upload(temp, tags)
            os.remove(temp)
            return a

    def data(self, encode=False):
        data = dict([(k,v.__data__()) for k,v in self.table.items()])
        return self.encoder(data) if encode else data

    def upload(self, file_local_address, tags):
        return upload_file(
            file_local_address,
            tags,
            self.project_name,
            self.private_key
        )

    def commit(self, message='',stdout=None):
        """
        Commit all changes into hg repository
        Note that local repo must be setup for access without key,
        and commit must not create new head, because push is not forced
        """
        u, r = self._hg(stdout)
        commands.addremove(u, r)
        commands.commit(u, r, message=message)
        commands.push(u, r)
        del u, r

    def summary(self, stdout=None):
        """
        Commit all changes into hg repository
        Note that local repo must be setup for access without key,
        and commit must not create new head, because push is not forced
        """
        u, r = self._hg(stdout)
        ctx = r[None]
        parents = ctx.parents()
        rev, branch = str(parents[0]), ctx.branch()
        del u, r
        return branch, rev

    def update(self, stdout=None):
        """
        Pull and update all changes from hg repository
        Note that this command destroy all local changes
        """
        u, r = self._hg(stdout)
        commands.pull(u, r)
        commands.update(u, r, clean=True)
        del u, r

    def branch(self, branch):
        u, r = self._hg()
        commands.update(u, r, branch)
        del u, r

    def branches(self, stdout=None):
        result = []
        try:
            u, r = self._hg(stdout)
            for n in r.heads():
                branch = r[n].branch()
                if branch not in result: result.append(branch)
            del u, r
        except:
            pass
        return result

    @property
    def tables(self):
        return self.table.keys()

    def html(self, per_page=10000):
        for i in self.table.values():
            i.html(per_page=per_page)

    def _hg(self, stdout=None):
        u = ui.ui()
        if stdout:
            u.fout = stdout
            u.ferr = stdout
        u.readconfig(os.path.join(self.path, '.hg', 'hgrc'))
        r = hg.repository(u, self.path)
        return u, r

