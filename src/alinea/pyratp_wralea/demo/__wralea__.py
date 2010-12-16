
# This file has been generated at Thu Dec 16 15:19:56 2010

from openalea.core import *


__name__ = 'PyRATP.demo'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.9.0'
__authors__ = ''
__institutes__ = None
__icon__ = ''


__all__ = ['_148689488']



_148689488 = CompositeNodeFactory(name='test_grid',
                             description='',
                             category='Unclassified',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('PyRATP', 'read grid'), 3: ('pyratp.data', 'grid3Da_2004.grd')},
                             elt_connections={  36852704: (3, 0, 2, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'read grid',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x8d21ad0> : "read grid"',
         'hide': True,
         'id': 2,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -269.0,
         'posy': -50.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   3: {  'block': False,
         'caption': 'grid3Da_2004.grd',
         'delay': 0,
         'factory': '<openalea.core.data.DataFactory object at 0x8d21810> : "grid3Da_2004.grd"',
         'hide': True,
         'id': 3,
         'lazy': True,
         'port_hide_changed': set([2]),
         'posx': -293.0,
         'posy': -112.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'delay': 0,
                'hide': True,
                'id': 0,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 0,
                'posy': 0,
                'priority': 0,
                'use_user_color': True,
                'user_application': None,
                'user_color': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'delay': 0,
                 'hide': True,
                 'id': 1,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 0,
                 'posy': 0,
                 'priority': 0,
                 'use_user_color': True,
                 'user_application': None,
                 'user_color': None}},
                             elt_value={  2: [],
   3: [  (0, 'PackageData(pyratp.data, grid3Da_2004.grd)'),
         (1, 'None'),
         (2, 'None')],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [-269.0, -50.0], 'userColor': None, 'useUserColor': False},
   3: {'position': [-293.0, -112.0], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




