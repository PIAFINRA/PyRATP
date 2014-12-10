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

################################################################
## Method to extract entity, xyz coordinates, surface area and nitrogen content from a scene
def SceneToRATP(scene,is_leaf=lambda x : True, display=None):
    IsLeafOrgan = {sh.id:is_leaf(sh) for sh in scene}
    print IsLeafOrgan

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

res = runRATP.DoIrradiation(grid, vegetation, sky, met)
[VegetationType,Iteration,day,hour,VoxelId,ShadedPAR,SunlitPAR,ShadedArea,SunlitArea]= res.T




