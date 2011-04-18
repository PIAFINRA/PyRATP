
# This file has been generated at Mon Apr 18 15:48:53 2011

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


__all__ = ['ratp_read_skyvault', 'ratp_DoAll', 'ratp_fill_grid', 'ratp_read_grid', 'ratp_read_vgx', 'ratp_read_vegetation', 'ratp_read_micrometeo']



ratp_read_skyvault = Factory(name='read_skyvault',
                authors=' (wralea authors)',
                description='read the skyvault file',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_skyvault',
                inputs=[{'interface': IFileStr(filter="*.skv", save=False), 'name': 'filename', 'value': None, 'desc': 'Skywvault file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_DoAll = Factory(name='do_all',
                authors=' (wralea authors)',
                description='run RATP',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='DoAll',
                inputs=[{'interface': ISequence, 'name': 'inputs', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'out', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_fill_grid = Factory(name='fill grid',
                authors=' (wralea authors)',
                description='fill a RATP Grid with vegetation',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='fill_grid',
                inputs=[{'interface': ISequence, 'name': 'entity', 'value': None, 'desc': '3d Grid file'}, {'interface': IFloat, 'name': 'x', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'y', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'z', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 's', 'value': None, 'desc': ''}, {'interface': None, 'name': 'n', 'value': None, 'desc': ''}, {'interface': None, 'name': 'grid', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_grid = Factory(name='read grid',
                authors=' (wralea authors)',
                description='Build a RATP Grid',
                category='simulation, ecophysiology',
                nodemodule='ratp',
                nodeclass='read_grid',
                inputs=[{'interface': IFileStr(filter="*.grd", save=False), 'name': 'filename', 'value': None, 'desc': '3d Grid file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_vgx = Factory(name='plant from vegestar',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_vgx',
                inputs=[{'interface': IFileStr(filter="*.vgx", save=False), 'name': 'filename', 'value': None, 'desc': 'Vegestar 3d Grid file'}],
                outputs=[{'interface': ISequence, 'name': 'entity', 'desc': 'No output for the moment'}, {'interface': IFloat, 'name': 'x', 'desc': ''}, {'interface': None, 'name': 'y', 'desc': ''}, {'interface': None, 'name': 'z', 'desc': ''}, {'interface': None, 'name': 's', 'desc': ''}, {'interface': None, 'name': 'n', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_vegetation = Factory(name='read_vegetation',
                authors=' (wralea authors)',
                description='read the vegetation files',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_vegetation',
                inputs=[{'interface': IFileStr(filter="*.vfn", save=False), 'name': 'filename', 'value': None, 'desc': 'Vegetation file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_read_micrometeo = Factory(name='read_micrometeo',
                authors=' (wralea authors)',
                description='read the micrometeo files',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='read_micrometeo',
                inputs=[{'interface': IFileStr(filter="*.mto", save=False), 'name': 'filename', 'value': None, 'desc': 'Micrometeo file'}],
                outputs=[{'interface': None, 'name': 'grid', 'desc': 'No output for the moment'}],
                widgetmodule=None,
                widgetclass=None,
               )




