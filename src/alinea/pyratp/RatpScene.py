""" A high level class interface to RATP
"""

import numpy
import pandas

from alinea.pyratp.grid import Grid
from alinea.pyratp.skyvault import Skyvault
from alinea.pyratp.vegetation import Vegetation
from alinea.pyratp.micrometeo import MicroMeteo
from alinea.pyratp.runratp import runRATP

from openalea.plantgl import all as pgl

class ColorMap(object):
    """A RGB color map, between 2 colors defined in HSV code

    :Examples: 

    >>> minh,maxh = minandmax([height(i) for i in s2])
    >>> colormap = ColorMap(minh,maxh)
    >>> s3 = [ Shape(i.geometry, Material
    >>>    (Color3(colormap(height(i))), 1), i.id)
    >>>    for i in s2]

    """

    def __init__(self, minval=0., maxval=1.):
        self.minval = float(minval)
        self.maxval = float(maxval)

    def color(self, normedU):
        """
        
        :param normedU: todo
        
        """
        inter = 1/5.
        winter = int(normedU/inter)
        a = (normedU % inter)/inter
        b = 1 - a
        
        if winter < 0:
            col = (self.coul2, self.coul2, self.coul1)
        elif winter == 0:
            col = (self.coul2, self.coul2*b+self.coul1*a, self.coul1)
        elif winter == 1:
            col = (self.coul2, self.coul1, self.coul1*b+self.coul2*a)
        elif winter == 2:
            col = (self.coul2*b+self.coul1*a, self.coul1, self.coul2)
        elif winter == 3:
            col = (self.coul1, self.coul1*b+self.coul2*a, self.coul2)
        elif winter > 3:
            col = (self.coul1, self.coul2, self.coul2)
        return (int(col[0]), int(col[1]), int(col[2]))

    def greycolor(self, normedU):
        """
        
        :param normedU: todo
        :returns: todo
        """
        return (int(255*normedU), int(255*normedU), int(255*normedU))

    def grey(self, u):
        """
        :param u: 
        :returns: todo
        """
        return self.greycolor(self.normU(u))

    def normU(self, u):
        """
        :param u:
        :returns: todo
        """
        if self.minval == self.maxval:
            return 0.5
        return (u - self.minval) / (self.maxval - self.minval)

    def __call__(self, u, minval=0, maxval=1, coul1=80, coul2=20):
        self.coul1 = coul1
        self.coul2 = coul2
        self.minval = float(minval)
        self.maxval = float(maxval)
        return self.color(self.normU(u))



def sample_database():
    """ to test if th creative commons database of french city fits
    """
    return {'Montpellier': {'city': 'Montpellier', 'latitude':43.61, 'longitude':3.87}}

class RatpScene(object):
    """ High level class interface for RATP
    """
    
    localisation_db = sample_database()
    default_grid = {'shape':[10, 10, 10], 'resolution':[0.1, 0.1, 0.1], 'z_soil':0}
    units = {'mm':0.001, 'cm': 0.01, 'dm': 0.1, 'm': 1, 'dam': 10, 'hm': 100, 'km':1000}
    timezone = 0 # consider UTC/GMT time for date inputs
    idecaly = 0 
    
    def __init__(self, scene=None, scene_unit = 'm', toric=False, entity=None, nitrogen=None, z_soil=None, localisation='Montpellier', grid_shape=None, grid_resolution=None, grid_orientation=0, z_resolution=None):
        """
        Initialise a RatpScene.
        
        Arguments:
        scene: a PlantGL Scene (list of shapes with ids)
        scene_unit (string): scene length unit ('m', 'cm', ...)
        toric (bool): False (default) if the scene is an isolated canopy, True if the scene is toric, ie simulated as if repeated indefinitvely 
        entity: a {scene_id:entity_key} dict that associate a scene object to an RATP entity. If None (default), all shapes points to entity_code 1.
        nitrogen: a {scene_id:entity_key} dict that associate a scene object to a nitrogen content. If None (default), all got a value of 2
        z_soil : z coordinate (scene units) of the soil in the scene. If None (default), soil will be positioned at the base of the canopy bounding box
        localisation : a string referencing a city of the localisation database (class variable), or a dict{'longitude':longitude, 'latitude':latitude}
        grid_shape: dimensions of the grid (voxel number per axis: [nx, ny, nz]). If None, shape will adapt to scene, using grid_resolution.
        grid_resolution: size (m) of voxels in x,y and z direction :[dx, dy, dz]. If None, resolution will adapt to scene using grid_shape.
        grid_orientation: angle (deg, positive clockwise) from X+ to North (default: 0).
        z_resolution (optional): tuple decribing individual voxel size (m) in z direction (from the soil to the top of the canopy). If None (default), grid_resolution is used.


        Note
        If scene is set to None, class default grid parameters are used to replace None values for grid_resolution and grid_shape
        If scene is provided and both grid_resolution and grid_shape are set to None,  the class default grid shape is used
        If both grid_resolution and grid_shape are provided, grid is build idependantly of scene content.
        """

        self.scene = scene
        self.scene_unit = scene_unit
        
        try:
            self.convert = RatpScene.units[scene_unit]
        except KeyError:
            print 'Warning, unit', scene_unit, 'not found, ratp assume that it is meters'
            self.convert = 1
            
        self.entity = entity
        if self.entity is None and self.scene is not None:
            self.entity = {sh.id:1 for sh in scene}
            
        self.nitrogen = nitrogen
        if self.nitrogen is None and self.scene is not None:
            self.nitrogen = {sh.id:2 for sh in scene}
        
        
        self.z_soil = z_soil
        if self.scene is None and self.z_soil is None:
            self.z_soil = RatpScene.default_grid['z_soil']
        
        if not isinstance(localisation, dict):
            try:
                self.localisation = RatpScene.localisation_db[localisation]
            except KeyError:
                print 'Warning : localisation',localisation, 'not found in database, using default localisation', RatpScene.localisation_db.iter().next()
                self.localisation = RatpScene.localisation_db.itervalues().next()
                
        self.grid_resolution = grid_resolution
        self.grid_shape = grid_shape
        
        if self.scene is None:
            if self.grid_resolution is None:
                self.grid_resolution = RatpScene.default_grid['resolution']
            if self.grid_shape is None:
                self.grid_shape = RatpScene.default_grid['shape']
        else:
            if self.grid_resolution is None and self.grid_shape is None:
                self.grid_shape = RatpScene.default_grid['shape']
            
        self.grid_orientation = grid_orientation
        self.z_resolution = z_resolution
        self.toric = toric
        
    def fit_grid(self, z_adaptive=False):
        """ Find grid parameters that fit the scene in the RATP grid
        """
        
        # fit regular grid to scene
        if self.scene is None:
            nbx, nby, nbz = self.grid_shape
            dx, dy, dz = self.grid_resolution # already in meter
            xo, yo, zsoil = 0, 0, 0 # origin
        else:
            # Find the bounding box that fit the scene
            tesselator = pgl.Tesselator()
            bbc = pgl.BBoxComputer(tesselator)
            bbc.process(self.scene)
            bbox = bbc.result

            zsoil = self.z_soil
            if zsoil is None:
                zsoil = bbox.getZMin() 
            htop = bbox.getZMax()
            xo = bbox.getXMin() * self.convert # origin    
            yo = bbox.getYMin() * self.convert
            if self.grid_resolution is not None and self.grid_shape is not None:
                nbx, nby, nbz = self.grid_shape
                dx, dy, dz = self.grid_resolution # already in meter
            else:
                if self.grid_resolution is None:
                    nbx, nby, nbz = self.grid_shape
                    dx = numpy.ceil(bbox.getXRange() / float(nbx) * self.convert * 100) / 100.
                    dy = numpy.ceil(bbox.getYRange() / float(nby) * self.convert * 100) / 100.
                    dz = numpy.ceil((htop - zsoil) / float(nbz) * self.convert * 100) / 100.
                if self.grid_shape is None: 
                    dx, dy, dz = self.grid_resolution
                    nbx = int(numpy.ceil(bbox.getXRange() * self.convert / float(dx)))
                    nby = int(numpy.ceil(bbox.getYRange() * self.convert / float(dy)))
                    nbz = int(numpy.ceil((htop - zsoil) * self.convert / float(dz)))

        # dz for all voxels    
        if self.z_resolution is not None:
            dz = self.z_resolution[::-1] # dz is from top to base for ratp
            nbz = len(dz)
        else:
            dz = [dz] * nbz
            
        grid_pars = {'njx':nbx, 'njy':nby, 'njz':nbz,
                     'dx':dx, 'dy':dy, 'dz':dz,
                     'xorig':xo, 'yorig':yo, 'zorig':-zsoil} # zorig is a z offset in grid.py (grid_z = z + zorig)
        
        return grid_pars
      
    def scene_transform(self):
        """ Transform scene for RATP input
        
            return entity, x,y,z,surface, nitrogen, sh_id lists
        """

        def _surf(mesh, iface):
            A,B,C = [mesh.pointList[i] for i in mesh.indexAt(iface)]
            return pgl.norm(pgl.cross(B-A, C-A)) / 2.0

        def _normal(mesh, iface):
            A,B,C = [mesh.pointList[i] for i in mesh.indexAt(iface)]
            n = pgl.cross(B-A, C-A)
            return n.normed()

        def _process(shape, discretizer):
            discretizer.process(shape)
            mesh = discretizer.result
            ifaces = range(mesh.indexListSize())
            s = [_surf(mesh,i) * self.convert**2 for i in ifaces]
            sh_id  = [shape.id] * len(s)
            n = [self.nitrogen[shape.id]] * len(s)
            entity = [self.entity[shape.id] - 1] * len(s) # entity 1 is encoded 0 in fill grid
            centers = [mesh.faceCenter(i) for i in ifaces]
            x, y, z = zip(*map(lambda x: (x[0] * self.convert, x[1] * self.convert, x[2] * self.convert), centers))

            return entity, x, y, z, s, n, sh_id
          
        d = pgl.Discretizer()
        transform = map(lambda x: _process(x,d), self.scene)
        return map(lambda what: reduce(lambda x,y : x+y, what), zip(*transform))

            
        
    def grid(self, rsoil=(0.075,0.20)):
        """ Create and fill a RATP grid 

        :Parameters:
        - rsoil : soil reflectances in the PAR and NIR band

        :Output:
            - grid3d : ratp fortran grid object
        """
    
        grid_pars = {'latitude': self.localisation['latitude'],
                     'longitude':self.localisation['longitude'],
                     'timezone': RatpScene.timezone,
                     'idecaly': RatpScene.idecaly,
                     'orientation': self.grid_orientation,
                     'toric': self.toric}
        
        grid_size = self.fit_grid()
        grid_pars.update(grid_size)
        
        entity, x, y, z, s, n, sh_id = self.scene_transform()
        nent = max(entity) + 1
        
        if not hasattr(rsoil, '__len__'):
            rsoil = [rsoil]
        
        grid_pars.update({'rs':rsoil,'nent':nent})
        
        grid = Grid.initialise(**grid_pars)
        grid, mapping = Grid.fill(entity, x, y, z, s, n, grid) # mapping is a {str(python_x_list_index) : python_k_gridvoxel_index}
        
        # in RATP output, VoxelId is for the fortran_k_voxel_index (starts at 1, cf prog_RATP.f90, lines 489 and 500)
        # here we return a python_x_list_index:fortran_k_voxel_index mapping
        # and one additional map that allows retrieving shape_id from python_x_index
        index = range(len(x))
        vox_map = {i:mapping[str(i)] + 1 for i in index}
        sh_map = {i:sh_id[i] for i in index}
        
        return grid, vox_map, sh_map

    def do_irradiation(self, rleaf=[0.1], rsoil=0.20, doy=1, hour=12, Rglob=1, Rdif=1):
        """ Run a simulation of light interception for one wavelength
        
            Parameters:            
                - rleaf : list of leaf refectance per entity
                - rsoil : soil reflectance
                - doy : [list of] day of year [for the different iterations]
                - hour : [list of] decimal hour (0-24) [for the different iterations]
                - Rglob : [list of] global (direct + diffuse) radiation [for the different iterations] (W.m-2)
                - Rdif : [list of] direct/diffuse radiation ratio [for the different iterations] (0-1)

        """
        
        grid, voxel_maping, shape_maping = self.grid(rsoil=rsoil)
               
        entities = [{'rf':[rf]} for rf in rleaf]
        vegetation = Vegetation.initialise(entities, nblomin=1)
        
        sky = Skyvault.initialise()
        
        met = MicroMeteo.initialise(doy=doy, hour=hour, Rglob=Rglob, Rdif=Rdif)

        res = runRATP.DoIrradiation(grid, vegetation, sky, met)
        
        VegetationType,Iteration,day,hour,VoxelId,ShadedPAR,SunlitPAR,ShadedArea,SunlitArea= res.T
        # 'PAR' is expected in  Watt.m-2 in RATP input, whereas output is in micromol => convert back to W.m2 (cf shortwavebalance, line 306)
        dfvox =  pandas.DataFrame({'VegetationType':VegetationType,
                            'Iteration':Iteration,
                            'day':day,
                            'hour':hour,
                            'VoxelId':VoxelId,
                            'ShadedPAR':ShadedPAR,
                            'SunlitPAR':SunlitPAR,
                            'ShadedArea':ShadedArea,
                            'SunlitArea': SunlitArea,
                            'Rinc': (ShadedPAR * ShadedArea + SunlitPAR * SunlitArea) / (ShadedArea + SunlitArea) / 4.6, 
                            })
        dfvox = dfvox[dfvox['VegetationType'] > 0]
        index = range(len(voxel_maping))
        dfmap = pandas.DataFrame({'scene_index': index,'shape_id':[shape_maping[i] for i in index], 'VoxelId':[voxel_maping[i] for i in index], 'VegetationType':[self.entity[shape_maping[i]] for i in index]})
    
        output = pandas.merge(dfmap, dfvox)
        output =  output.sort('scene_index') # sort is needed to ensure matching with triangulation indices
        
        return output
        
    def plot(self, output, minval=None, maxval=None):
        par = output['Rinc']
        if minval is None:
            minval = min(par)
        if maxval is None:
            maxval = max(par)
        cmap = ColorMap()
        
        scene= pgl.Scene()
        discretizer = pgl.Discretizer()
        
        for sh in self.scene:
            discretizer.process(sh)
            mesh = discretizer.result
            mesh.colorList = []
            mesh.colorPerVertex = False
            colors = map(lambda x: cmap(x,minval,maxval,250., 20.), par[output['shape_id'] == sh.id])
            for color in colors:
                r, g, b = color
                mesh.colorList.append(pgl.Color4(r, g, b, 0))
                
            scene.add(mesh)
            
        pgl.Viewer.display(scene)
        
        return scene
            
