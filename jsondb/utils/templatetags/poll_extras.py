# -*- coding: utf-8 -*-
from django import template
import re,string
register = template.Library()

@register.filter(name='get')
def geta(value, arg):
    return value.get(arg)


@register.filter(name='int')
def intg(value):
    return int(value)

@register.filter(name='str')
def strg(value):
    return str(value)

@register.filter(name='help_text')
def help_text(value, arg):
    return value.structure(arg)['$format'].get('text') or arg

@register.filter(name='foreign')
def foreign(value, arg):
    try:
        key = value.t.structure(arg)['$format'].get('forign_key')
        return value.core.tables[key].get( value.get(arg) )
    except:
        return None

@register.tag
def make_list(parser, token):
  bits = list(token.split_contents())
  if len(bits) >= 4 and bits[-2] == "as":
    varname = bits[-1]
    items = bits[1:-2]
    return MakeListNode(items, varname)
  else:
    raise template.TemplateSyntaxError("%r expected format is 'item [item ...] as varname'" % bits[0])

class MakeListNode(template.Node):
  def __init__(self, items, varname):
    self.items = map(template.Variable, items)
    self.varname = varname

  def render(self, context):
    context[self.varname] = [ i.resolve(context) for i in self.items ]
    return ""
