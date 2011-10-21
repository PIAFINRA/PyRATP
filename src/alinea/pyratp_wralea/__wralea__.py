
# This file has been generated at Thu Oct 13 11:32:38 2011

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


__all__ = ['ratp_read_skyvault', 'ratp_DoAll', 'ratp_fill_grid', 'ratp_read_grid', 'ratp_read_vgx', 'ratp_read_vegetation', 'ratp_read_micrometeo', 'extract_leaves',
'extract_time', 'extract_spatial']



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
                outputs=[{ 'name': 'time_spatial', 'desc': 'time evolution for each voxel'}, { 'name': 'tree', 'desc': 'time evolution for each voxel'}],
                widgetmodule=None,
                widgetclass=None,
               )




ratp_fill_grid = Factory(name='fill grid',
                authors=' (wralea authors)',
                description='fill a RATP Grid with vegetation',
                category='Unclassified',
                nodemodule='ratp',
                nodeclass='fill_grid',
                inputs=[{'interface': IInt, 'name': 'entity', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'x', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'y', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'z', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 's', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'n', 'value': None, 'desc': ''}, {'interface': None, 'name': 'grid', 'value': None, 'desc': ''}],
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
                outputs=[{'interface': IInt, 'name': 'entity', 'desc': ''}, {'interface': IFloat, 'name': 'x', 'desc': ''}, {'interface': IFloat, 'name': 'y', 'desc': ''}, {'interface': IFloat, 'name': 'z', 'desc': ''}, {'interface': IFloat, 'name': 's', 'desc': ''}, {'interface': IFloat, 'name': 'n', 'desc': ''}],
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


extract_leaves =  Factory(name='extract leaves',
                authors=' (wralea authors)',
                category='Mtg, light',
                nodemodule='ratp',
                nodeclass='extract_leaves',
                inputs=[{ 'name': 'mtg', 'desc': 'MTG file'}, 
                        dict(name='scaling factor', value=100, interface='IFloat'),
                        dict(name='nitrogen', value=2., interface='IFloat'),
                        ],
                outputs=[dict(name='leaves_id', desc='vertex id for leaves '), 
                         dict(name='entity', desc='the vegetation type'), 
                         dict(name='X', desc='X coordinate'), 
                         dict(name='Y', desc='Y coordinate'), 
                         dict(name='Z', desc='Z coordinate'), 
                         dict(name='leaf area', desc='leaf area'), 
                         dict(name='leaf nitrogen', desc='leaf nitrogen'), 
                         ],
               )
extract_time=  Factory(name='extract time',
                authors=' (wralea authors)',
                category='Mtg, light',
                nodemodule='ratp',
                nodeclass='ExtractTime',
               )
extract_spatial=  Factory(name='extract spatial',
                authors=' (wralea authors)',
                category='Mtg, light',
                nodemodule='ratp',
                nodeclass='ExtractTime',
               )

