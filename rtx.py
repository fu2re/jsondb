from jsondb import JsonDB
#
#o = JsonDB('/home/fu2re/Documents/content/tycoon_content')
#print o.table['progress'].get(1).validate()
#print o.table['progress'].get(1).errors
#o.private_key = '3a232aebc46b6065e9f9855410e9d474'
#    my_experiment.user_password = 'PRESC0tt'
#print o.upload('/home/fu2re/Desktop/9d52ec54.jpg', 'building_home, preview') 
o = JsonDB('/home/fu2re/Documents/content/tycoon_content')
#pt = o.table['quest'].structure('app.quests.$items').copy()
#pt['$format'] = pt['$format'].copy()
#pt['$format'].update(aaaa=12)
#print o.table['quest'].template['app']['quests']['$items']['$format']['aaaa']

#o.table['quest'].change('app.quests.$items', False, foreign_key='quest')
#print o.table['quest'].template['app']['quests']['$items']['$format']['foreign_key']
#from jsondb.csv2json import *
#parser = Parser(
#     '/home/fu2re/quest_0602.csv',
#     api = o,
#     table = 'quest',
#     delimiter=';')
#parser.execute()

#o.table['building_home'].remove('state.$items.lock', False)
#print not 'lock' in o.table['building_home'].get(10).get('state.0').keys()
#for i in o.table['building_home'].objects.values():
#    for ii in i.get('state'):
#        i.remove('state.%s.lock' % ii)


#import os
#from data.stdout import FakeStdout
#from mercurial import ui, hg, commands
#path = '/home/fu2re/Documents/content/hw'
#
#
#f = FakeStdout()
#u = ui.ui()
#u.fout = u.ferr = f
#u.readconfig(os.path.join(path, '.hg', 'hgrc'))
#r = hg.repository(u, path)
#commands.pull(u, r)
#commands.update(u, r, clean=True)
#print '___________'
#print f.read()
#f.close()


#commands.push(u, r)

#print process.communicate()[0]
