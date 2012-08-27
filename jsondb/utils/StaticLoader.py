# coding: utf8
import logging
import os
import json
import re

from jsondb.model.StaticModel import StaticModel

class StaticLoader(object):

    mapper = {  }

    def __init__(self, path):
        self.path = os.path.join(path, 'balance')

    def collections(self):
        return os.listdir(self.path)

    def join(self, *items):
        return os.path.join(self.path, *items)

    def files(self, collection):
        path = self.join(collection)
        list_dir = os.listdir(path)
        return [i for i in list_dir if re.match('^[\d]*.json$',i)]

    def split_id(self, file):
        return int(os.path.splitext(file)[0])

    def load(self, collection, file):
        assign_model = self.mapper.get(collection, StaticModel)
        path = self.join(collection, file)
        logging.info('load model_file %s' % path)
        try:
            data = json.JSONDecoder('utf-8').decode(open(path).read())
        except:
            raise ValueError("Can't read file: %s" % path)
        
        data['id'] = self.split_id(file)

        return assign_model(data)
    
    def load_from_data(self, collection, data, id):
        assign_model = self.mapper.get(collection, StaticModel)
        data['id'] = id

        return assign_model(data)

    def models(self, collection):
        result = {}
        
        for file in self.files(collection):
            model = self.load(collection, file)
            result[model.id] = model

        return result

