# Header
#

"""

"""

##from alinea.pyratp import pyratp
import pyRATP
import numpy as np

class Grid(object):
    """
    """
    def __init__(self, *args, **kwds):
        """

        """
        pass


    @staticmethod
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

    def fill(self, entity, x, y, z, s, n):
        """ Filling the 3D Grid with points, area and nitrogen content.

        :Parameters:
            - `x`: an array of abscisse.
            - .
        """

        if entity.max() > grid3d.nent:
            raise ValueError('Number of entity is too great')

        if s.min() < 0.:
            raise ValueError('Negative area value is prohibited')

        ztot = grid3d.dz.sum()
        if z.max() > ztot:
            raise ValueError('Some Z points are outside of the grid')

        grid3d.volume_canopy = 0.
        grid3d.s_canopy=0.
        grid3d.s_vx=0.
        grid3d.s_vt=0.
        grid3d.s_vt_vx=0.
        grid3d.n_canopy=0.

        grid3d.nemax = 1

        nft, k = 0, 0

        xx -= grid3d.xorigin
        yy -= grid3d.yorigin
        zz -= grid3d.zorigin

        if zz.min() < 0.:
            raise ValueError('Some elements have a negative Z value.')

        nft = entity.len()
        grid3d.n_canopy = (n*s).sum()
        grid3d.s_canopy = s.sum()

        # sum the surface of each element of the same entity
        for i in range(grid3d.nent):
            grid3d.s_vt[i] = s[entity==i].sum()

        dx, dy = grid3d.dx, grid3d.dy
        # Compute the coord of each element in the grid.
        # modulo is used to build a toric scene.
        jx = np.array(x/dx, dtype=np.int)%njx
        jy = np.array(y/dy, dtype=np.int)%njy
        jz = np.zeros_like(z,dtype=np.int)
        zzz = grid3d.dz.cumsum()
        jz = zzz.len()-1
        for i in range(zzz.len()-1):
            mask = zzz[i]<= z < zzz[i+1]
            jz[mask] = i
        # TO CONTINUE (line 318)


def vegestar(filename): pass

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
