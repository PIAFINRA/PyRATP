"""""""""""
  Test LIGHT pyRATP

"""""""""""


import openalea.plantgl.all as pgl
import numpy as np
from alinea.pyratp.skyvault import Skyvault
from alinea.pyratp.grid import Grid
from alinea.pyratp.vegetation import Vegetation
from alinea.pyratp.micrometeo import MicroMeteo
from alinea.pyratp.runratp import runRATP
from alinea.pyratp.RATP2VTK import RATP2VTK
from alinea.pyratp_wralea.ExtractLight import *

from mtg.plantframe.color import colormap

def plot3d(g):
    """
    TODO: move to vplants.newmtg?

    Returns a plantgl scene from an mtg.
    """
    import openalea.plantgl.all as pgl

    Material = pgl.Material
    Color3 = pgl.Color3
    Shape = pgl.Shape
    Scene = pgl.Scene

    colors = g.property('color')
    geometries = g.property('geometry')

    scene = Scene()

    def geom2shape(vid, mesh, scene):
        shape = None
        if isinstance(mesh, list):
            for m in mesh:
                geom2shape(vid, m, scene)
            return
        if mesh is None:
            return
        if isinstance(mesh, Shape):
            shape = mesh
            mesh = mesh.geometry

        if colors:
            shape = Shape(mesh, Material(Color3(* colors.get(vid, [0,0,0]) )))

        shape.id = vid
        scene.add(shape)

    for vid, mesh in geometries.iteritems():
        geom2shape(vid, mesh, scene)
    pgl.Viewer.display(scene)
    return scene

################################################################
## Method to extract entity, xyz coordinates, surface area and nitrogen content from a scene
def SceneToRATP(scene,is_leaf=lambda x : True, display=None):
    IsLeafOrgan = {sh.id:is_leaf(sh) for sh in scene}
##    print IsLeafOrgan

    ## View/Check the scene
    if display:
        pgl.Viewer.display(scene)

    ###### Scene to RATP
    #Area
    sLeaf =np.array(map(pgl.surface, scene))
    #If not a Leaf: sLeaf/2

    #Leaf Nitrogen (g/m2)
    n = np.ones(len(sLeaf))*2.0

    #Leaf Id
    entity = np.zeros(len(sLeaf))

    #Leaf coordinates
    krikri = pgl.Discretizer()
    XYZLeaf=[]
    #Coordinates
    for sc in scene:
        krikri.process(sc)
        mesh=krikri.result
        XYZLeaf.append(mesh.pointList.getCenter())

    gg = np.array(XYZLeaf)

    return entity,gg.T[0]/100.,gg.T[1]/100.,-gg.T[2]/100.,sLeaf/10000.,n
################################################################

#### Initialize all input files except the 3D plant
gridfile='grid3Da_2004.grd'
vfnfile='vegetationa_2004.vfn'
skyfile='skyvaultsoc.skv'
metfile='mmeteo082050_1h.mto'
outfile='output.txt'
##mapfile='mapratp_%s.txt'%(date)

#### Get the scene
scene = pgl.Scene(r"C:\pommier.geom")

import openalea.mtg as mtg
g = mtg.MTG()
vid = g.add_component(g.root)
mtg.random_tree(g, vid, nb_vertices=len(scene))
g.properties()['geometry'] = {sh.id+1:sh for sh in scene}

####Get objects in pyRATP fillgrid format
entity,x,y,z,s,n = SceneToRATP(scene)

#####Set the grid
grid = Grid.read(gridfile)

#### Fill grid
grid,map = Grid.fill(entity, x, y, z, s, n, grid)

#### Vegetation Type
vegetation = Vegetation.read(vfnfile)

#### Sky
sky = Skyvault.read(skyfile)

#### Meteo
met = MicroMeteo.read(metfile)

## Run PyRATP -  Light part
##res = runRATP.DoAll(grid, vegetation, sky, met)
res = runRATP.DoIrradiation(grid, vegetation, sky, met)
[VegetationType,Iteration,day,hour,VoxelId,ShadedPAR,SunlitPAR,ShadedArea,SunlitArea]= res.T

rr = res.T[1:]
rr2 = rr.T

## Associate Voxel Values to Scene objects
VarResu = ExtractLight(map, rr2, 234, 11, 6)
VarRS ={i+1:v for i,v in enumerate(VarResu)}
##print VarResu

## Plot the result

# 3. Update mtg with light_star
g.properties()['VarResu'] = VarRS

# 4. Add a color property to the mtg and view the result on a plot 3D
g = colormap(g, 'VarResu', cmap='jet', lognorm=True)
plot3d(g)


