# coding: utf8
import httplib

def url_exists(site, path):
    conn = httplib.HTTPConnection(site)
    conn.request('HEAD', path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200


class Check( object ):
    deprecated = {
        'str':('foreign_key','dynamic'),
        'int':('dynamic','is_file'),
        'float':('foreign_key','dynamic','is_file'),
        'list':('foreign_key','dynamic','values','is_file'),
        'dict':('foreign_key','values','is_file','min','max'),
        'ddict':('values','is_file')
    }

    def check_value_length(self, field, value):
        self.check_min(field, value)
        self.check_max(field, value)

    def check_min(self, field, value, future=False):
        if field.min:
            min = field.min - 1 if future else field.min
            if field.kind in ('str', 'list', 'ddict') and not min <= len(value or []) or \
            field.kind in ('int','float') and not min <= value:
                raise ValueError("Depracated length value in %s" % field.target)

    def check_max(self, field, value):
        if field.max:
            if field.kind in ('str', 'list', 'ddict') and not len(value or []) <= field.max or \
            field.kind in ('int','float') and not value <= field.max:
                raise ValueError("Depracated length value in %s" % field.target)


    def check_value_default(self, field, value=None, ignoredefault=False, ignorelength=False):
        if value is None:
            value = field.default

        if field.kind in ('dict', 'list', 'ddict') and value and not ignoredefault:
            raise ValueError("Dict and list fields, doesn't support default value %s" % field.target)

        elif field.kind == 'str' and type(value) not in (str,unicode) or \
        field.kind == 'int' and type(value) != int or \
        field.kind == 'float' and type(value) not in (int, float):
            raise TypeError("Type value error at %s, %s" % (field.target, value))

        if not ignorelength:
            self.check_value_length(field, value)

        if field.values:
            if value not in field.values:
                raise ValueError("Depracated default value in %s" % field.target)

#        if field.is_file:
#            if not url_exists(self.core.remote_static_server, value):
#                raise ValueError(
#                    "Url %s/%s doesn't exist at %s" % \
#                    (self.core.remote_static_server, value, field.target)
#                )


    def check_params(self, field):
        if field.kind not in self.deprecated:
            raise TypeError("Unknown type %s at %s" % (field.kind, field.target))
        
        elif set(field.pattern.keys()) & set(self.deprecated[field.kind]):
            raise ValueError(
                "Deprecated property in %s: %s" % (
                field.target,
                set(field.pattern.keys()) - set(self.deprecated[field.kind]))
            )

        elif field.max and field.min:
            if not field.min <= field.max:
                raise ValueError(
                    "Min must be smaller then max in %s" %
                    field.target
                )



    def check_add(self, field, terminate):
        if not self.structure(field.target):
            raise KeyError("Field %s does't exist" % field.target)

        if field.kind != 'dict':
            raise TypeError("Wrong type, %s is not dict" % field.target)

#        if tp['$format'].get('kind') == 'dict' and tp.get('dynamic'):
#            raise TypeError("Wrong type, cannot add model in %s" % target)

        if self.structure(terminate):
            raise KeyError("Field %s already exist" % terminate)
        
        if field.kind in ('int', 'str', 'float') and field.default:
            raise ValueError("Default requres for %s" % field.target)

    def check_foreign_key(self, field, targets):
        if field.foreign:
            keys = []
            if field.kind == 'int':
                filter = '%s__in' 
                self.core.check_foreign_key(
                    field.foreign, field.default, field.target
                )
                for doc in self.objects.values():
                    for target in targets:
                        key = doc.get(target)
                        if key is not None and key not in keys:
                            keys.append(int(key))

            elif field.kind == 'ddict':
                filter = '%s__haskey'
                for doc in self.objects.values():
                    for target in targets:
                        v = doc.get(field.target)
                        if v is not None:
                            keys.extend([int(k) for k in v.keys() if k not in keys])
                
            diff = set(keys) - set(self.core.table[field.foreign].objects.keys())
            if diff:
                diffdoc = [i.id for i in self.filter(filter % field.target, list(diff))]
                if not diffdoc:
                    for target in targets:
                        diffdoc.extend([i.id for i in self.filter(filter % target, list(diff))])
                raise KeyError(
                    'some keys not presents in table "%s": ERROR in %s' % (field.foreign, diffdoc)
                )

class CoreCheck( object ):

    def check_foreign_key(cls, foreign_key, value, target):
        if foreign_key:
            if not cls.table.get(foreign_key):
                raise KeyError("Table %s does't exist, %s" % (foreign_key, target))
            elif not cls.table[foreign_key].get(value):
                raise KeyError("Table %s hasn't key %s, %s" % (foreign_key, value, target))

