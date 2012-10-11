from openalea.core import *

from alinea.pyratp import skyvault
from alinea.pyratp import grid
from alinea.pyratp import vegetation
from alinea.pyratp import micrometeo
from alinea.pyratp import runratp
from alinea.pyratp import mtg_extract
from alinea.pyratp import can2riri
from alinea.pyratp.RATP2VTK import RATP2VTK



read_grid = grid.Grid.read
read_vgx = grid.Grid.readVgx
fill_grid = grid.Grid.fill

read_skyvault = skyvault.Skyvault.read
read_vegetation = vegetation.Vegetation.read
read_micrometeo = micrometeo.MicroMeteo.read

DoAll = runratp.runRATP.DoAll
DoIrradiation = runratp.runRATP.DoIrradiation
extract_leaves = mtg_extract.extract_leaves
can2riri = can2riri.can2riri

class ExtractColumn( Node ):
    """ Extract column based on str
    """
    header = ['']
    index = [0]

    def __init__(self):

        Node.__init__(self)

        funs= self.header
        self.add_input( name = "column", interface = IEnumStr(funs), value = funs[0])
        self.add_input( name = "array" )
        self.add_output( name = "array", interface = None)

    def __call__(self, inputs):
        col= self.get_input("column")
        a = self.get_input("array")
        i = self.index[self.header.index(col)]

        self.set_caption(col)

        return a[:,i],

class ExtractTime(ExtractColumn):
    header = """iteration
    day
    hour
    entity
    radiation (w/m2)
    Air Temperature
    Photosynthesis
    Transpiration
    """.split('\n')
    index = [0,1,2,3,4,50, 96, 97]
    def __init__(self):

        ExtractColumn.__init__(self)


class ExtractSpatial(ExtractColumn):
    header = """iteration
    day
    hour
    Air Temperature
    Voxel id
    Leaf Temperature (shaded)
    Leaf Temperature (sunlit)
    Photosynthesis (shaded)
    Photosynthesis (sunlit)
    Transpiration (shaded)
    Transpiration (sunlit)
    Leaf surface (shaded)
    Leaf surface (sunlit)
    """.split('\n')
    index = range(len(header))

    def __init__(self):
        ExtractColumn.__init__(self)

    def __call__(self, inputs):
        col= self.get_input("column")
        a = self.get_input("array")
        i = self.index[self.header.index(col)]

        self.set_caption(col)

        # TODO extract the values for each voxel
        return a[:,i],

