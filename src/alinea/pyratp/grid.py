# Header
#

"""

"""

from alinea.pyratp import pyratp
import numpy as np

class Grid(object):
    """
    """
    def __init__(self, *args, **kwds):
        """

        """
        pass


def read(filename):
    """ Creating the 3D grid from  input file. """

    grid3d = pyratp.grid3d

    f = open(filename)

    # number of grid voxels along X Y and Z axis
    _read(f, grid3d.njx, grid3d.njy, grid3d.njz)

    #allocated to (njz+1) as needed in beampath
    grid3d.dz = np.zeros(grid3d.njz+1)

    # voxel size according to X- Y- and Z- axis
    # TEST
    _read(f, grid3d.dx, grid3d.dy, *grid3d.dz[:-1])
    
    # 3D grid origin
    _read(f, grid3d.xorig, grid3d.yorig, grid3d.zorig)

    _read(f, grid3d.latitude, grid3d.longitude, grid3d.timezone)

    # angle (degree) between axis X+ and North
    _read(f, grid3d.orientation)

    # offset between canopy units along Y-axis
    #      idecaly <> 0 : plantation en quinconce partiel (ie, decalage des Y
    #      d'un nombre entier idecaly de cellules Y d'une maille a l'autre).
    #             si idecaly = njy / 2 : quinconce parfait
    #             si idecaly = 0       : plantation orthogonale
    #      Cf. Subroutine Beampath
    _read(f, grid3d.idecaly)

    # nent: number of vegetation types in the 3D grid
    _read(f, grid3d.nent)

    # number of wavelength bands for the soil surface
    l = f.readline().split('!')[0].strip().split(' ')
    assert len(l) == int(l[0])+1
    grid3d.nblosoil = l[0]
    grid3d.rs = np.array(l[1:], dtype=np.float)

    f.close()

    # definition of aliases
    njx, njy, njz = grid3d.njx, grid3d.njy, grid3d.njz
    dx, dy = grid3d.dx, grid3d.dy
    kxyz = grid3d.kxyz
    numx, numy, numz, nje = grid3d.numx, grid3d.numy, grid3d.numz, grid3d.nje
    leafareadensity, N_detailed, nume = grid3d.leafareadensity, grid3d.n_detailed, grid3d.nume
    nent = grid3d.nent
    S_vt_vx = grid3d.s_vt_vx
    S_vx = grid3d.s_vx
    S_vt = grid3d.s_vt
    volume_canopy = grid3d.volume_canopy
    voxel_canopy = grid3d.voxel_canopy

    nvegmax = njx * njy * njz

    xrang = njx * dx
    yrang = njy * dy
    grid3d.total_ground_area=xrang*yrang

    grid3d.kxyz = np.zeros(njx*njy*(njz+1)).reshape((njx, njy, njz+1))
    grid3d.numx = np.zeros(nvegmax)
    grid3d.numy = np.zeros(nvegmax)
    grid3d.numz = np.zeros(nvegmax)
    grid3d.nje = np.zeros(nvegmax)

    grid3d.leafareadensity= np.zeros(nent*nvegmax).reshape(nent, nvegmax)
    grid3d.n_detailed = np.zeros(nent*nvegmax).reshape(nent, nvegmax)
    grid3d.nume = np.zeros(nent*nvegmax).reshape(nent, nvegmax)
    
    # Leaf area (m^2) per voxel and vegetation type
    grid3d.S_vt_vx =  np.zeros(nent*nvegmax).reshape(nent, nvegmax)
    # Leaf area (m^2) per voxel 
    grid3d.s_vx = np.zeros(nvegmax)
    # Leaf area (m^2) per vegetation type
    grid3d.s_vt = np.zeros(nent)

    grid3d.volume_canopy = np.zeros(nent+1)
    grid3d.voxel_canopy = np.zeros(nent)

def _read(f, *args):
    print '_read (',args,')'
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l = l.strip().split(' ')
    l = filter(None,l)
    print l
    assert len(args) <= len(l)

    args = list(args)
    for i in range(len(args)):
        args[i].fill(l[i])
    print args
    return
