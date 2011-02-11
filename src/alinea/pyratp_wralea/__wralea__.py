
# This file has been generated at Thu Dec 16 15:03:49 2010

from openalea.core import *


__name__ = 'PyRATP'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.9.0'
__authors__ = ''
__institutes__ = None
__icon__ = ''


__all__ = ['read_grid_read_grid', 'read_vgx_grid']



read_grid_read_grid = Factory(name='read grid',
                authors=' (wralea authors)',
                description='Build a RATP Grid',
                category='simulation, ecophysiology',
                nodemodule='ratp',
                nodeclass='read_grid',
                inputs=[{'interface': IFileStr(filter='*.grd'), 'name': 'filename', 'value': None, 'desc': '3d Grid file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )

read_vgx_grid = Factory(name='grid from vegestar',
                authors=' (wralea authors)',
                category='simulation, ecophysiology',
                nodemodule='ratp',
                nodeclass='read_vgx',
                inputs=[{'interface': IFileStr(filter='*.vgx'), 'name': 'filename', 'value': None, 'desc': 'Vegestar 3d Grid file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
               )



