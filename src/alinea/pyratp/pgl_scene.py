""" Interfaces for using PlantGl scene with RATP
"""
import numpy

from alinea.pyratp.grid import Grid
from openalea.plantgl import all as pgl
from math import ceil


class PglGrid(object):
    """ Interface between PlantGL scene and RATP grid
    """
    
    def __init__(self, scene, dx=0.2, dy=0.2, dz=0.2, convert=1, latitude=43.61, longitude=3.87, north=0, zsoil=0):
        """
        Setup parameters that fit a PlantGL scene in a RATP grid. No grid is created nor filled at initialisation.
        
        PlantGL Scene coordinate system is Z+ pointing upward, hence with counter-clockwise positive angles in the XY plane (ie North -> West)
        RATP grid coordinate system is Z+ pointing downward with clockwise positive angles in the XY plane (North -> East)
        RATP coordinate system is required for a correct orientation of sun and sky beams.
        In this class, the RATP grid coordinate system is set at the top left corner of the scene bounding box, Z+ downward (opposite scene Z+), X+ left-> right (same as scene X+), Y+ back -> front (opposite scene Y+)
        RATP grid is configured for UTC/GMT time.
        
        Arguments:
        dx, dy, dz : size of voxels in x,y and z direction in the scene coordinate system / scene unit
        convert : multiplication factor from scene units to meters (eg 0.01 if scene unit is centimeter)
        latitude and longitude of the secene (deg)
        north: signed angle (deg) from X+ to North in the scene coordinate system (positive counter-clockwise)
        zsoil : altitude of the soil in the scene in the secene coordinate system
        """

        # Find the bounding box that fit the scene
        tesselator = pgl.Tesselator()
        bbc = pgl.BBoxComputer(tesselator)
        bbc.process(scene)
        bbox = bbc.result

        # compute number of cells along axes
        htop = bbox.getZMax()
        zsoil = min(zsoil,bbox.getZMin()) # no roots !
        nbz = int(ceil((htop - zsoil) / float(dz)))
        nbx = int(ceil(bbox.getXRange() / float(dx)))
        nby = int(ceil(bbox.getYRange() / float(dy)))
        
        # scene coordinates of RATP coordinates origin
        xo = bbox.getXMin()
        yo = bbox.getYMax()
        zo = zsoil + nbz * dz
        
        self.grid_pars = {'njx':nbx, 'njy':nby, 'njz':nbz,
                     'dx':dx * convert, 'dy':dy * convert, 'dz': [dz * convert] * nbz,
                     'xorig':0, 'yorig':0, 'zorig':0, # coordinate transforms are handled during grid filling
                     'latitude': latitude,
                     'longitude':longitude,
                     'timezone':0,# consider UTC/GMT time
                     'idecaly':0,
                     'orientation': - north}# in RATP orientation is the angle from X+ to North, positive clockwise.

        self.xo = xo
        self.yo = yo
        self.zo = zo
        self.zsoil = zsoil
        self.convert = convert
        
    def transform(self, x, y, z):
        """ Coordinate transform from scene to grid
        """
        newx = (numpy.array(x) - self.xo) * self.convert
        newy = - (numpy.array(y) - self.yo) * self.convert
        #newz = - (numpy.array(z) - self.zo) * self.convert
        newz = (numpy.array(z) - self.zsoil) * self.convert # grid.py fill the grid from top to base already
        return newx, newy, newz

    def grid(self, scene, entity=None, stem=None, nitrogen=None, rsoil=(0.075,0.20)):
        """ Create and fill a RATP grid with the objects found in scene
        

        :Parameters:
        - scene : A plantGL scene
        - entity: a mapping of scene_id to entity_id (vegetation type). If None (default), all scene objects are mapped to entity 0
        - stem: a mapping of scene_id to True/False indicating if the primitive is a stem. If None (default), all scene objects are mapped to False (ie considered as leaves)
        - nitrogen: a mapping of scene_id nitrogen content (g/m2). If None (default), all scene objects are mapped to 2 g/m2
        - rsoil : soil reflectances in the PAR and NIR band

        :Output:
            - grid3d : ratp fortran grid object
        """
    
        #Area
        s = numpy.array(map(pgl.surface, scene)) * self.convert**2
        #If not a Leaf: sLeaf/2

        #Nitrogen (g/m2)
        n = numpy.ones(len(s))*2.0


        
        #coordinates
        krikri = pgl.Discretizer()
        XYZLeaf=[]
        sh_id=[]
        for sc in scene:
            krikri.process(sc)
            mesh=krikri.result
            XYZLeaf.append(mesh.pointList.getCenter())
            sh_id.append(sc.id)
        xyz = numpy.array(XYZLeaf)
        x, y, z = self.transform(xyz.T[0], xyz.T[1], xyz.T[2])
        
                #entities 
        if entity is None:
            entity = numpy.zeros(len(s))
        else:
            entity = numpy.array([entity[sh_id[i]] for i in range(len(sh_id))])
        nent = max(entity) + 1
        
        self.grid_pars.update({'rs':rsoil,'nent':nent})
        
        grid = Grid.initialise(**self.grid_pars)
        grid, mapping = Grid.fill(entity, x, y, z, s, n, grid) # mapping is a {str(python_x_list_index) : python_k_gridvoxel_index}
        
        # in RATP output, VoxelId is for the fortran_k_voxel_index (starts at 1, cf prog_RATP.f90, lines 489 and 500)
        # here we return shape_id:fortran_k_voxel_index
        newmap = {sh_id[i]:mapping[str(i)] + 1 for i in range(len(sh_id))}
        
        return grid, newmap
    
