# Header
#

"""

"""

from alinea.pyratp import pyratp
#import pyRATP
import numpy as np
import vege3D
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
        _read(f, grid3d.dx, grid3d.dy, grid3d.dz[:-1])
        print 'grid3d.dx',grid3d.dx
        print 'grid3d.dz',grid3d.dz
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

        nent = grid3d.nent
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
        grid3d.s_vt_vx =  np.zeros(nent*nvegmax).reshape(nent, nvegmax)
        # Leaf area (m^2) per voxel
        grid3d.s_vx = np.zeros(nvegmax)
        # Leaf area (m^2) per vegetation type
        grid3d.s_vt = np.zeros(nent)

        grid3d.volume_canopy = np.zeros(nent+1)
        grid3d.voxel_canopy = np.zeros(nent)
        return grid3d

    @staticmethod
    def readVgx(filename):
        """ Filling the 3D Grid with points, area and nitrogen content.

        :Parameters:
            - `x`: an array of abscisse.
            - .
        """
        tv,tx,ty,tz,ts,tn = vege3D.Vege3D.readVGX(filename)
        return tv,tx,ty,tz,ts,tn


    @staticmethod
    def fill(entity, x, y, z, s, n ,grid):
##        print entity, x, y, z, s, n
        """ Filling the 3D Grid with points, area and nitrogen content.
        lkjfkjrzelkrjzelrkjzer
        :Parameters:
            - `x`: an array of abscisse.
            - .
##        """


        if entity.max() >  grid.nent:
            raise ValueError('Number of entity is too great')

        if s.min() < 0.:
            raise ValueError('Negative area value is prohibited')

        ztot = grid.dz.sum()
        if z.max() > ztot:
            raise ValueError('Some Z points are outside of the grid')

        grid.nemax = 1
        nft, k = 0, 0

        nft = np.alen(entity)
        grid.n_canopy = (n*s).sum()
        grid.s_canopy = s.sum()
         # sum the surface of each element of the same entity
        for i in range(grid.nent-1):
            grid.s_vt[i] = s[entity==i].sum()

        dx, dy , dz = grid.dx, grid.dy, grid.dz
        #dh: tableau des hauteurs z
        dh = np.array(0)
        for i in range(np.alen(dz)-1):
            dh=np.append(dh,dz[:i+1].sum()+grid.zorig)
        dh=np.delete(dh,0)
        print 'dh',dh
        for i in range(np.alen(x)):
            x[i] = x[i]/100 - grid.xorig
            y[i] = y[i]/100 - grid.yorig
            z[i] = -z[i]/100 + grid.zorig
            if z[i].min() < 0.:
                raise ValueError('Some elements have a negative Z value.')


            # Compute the coord of each element in the grid.
            # modulo is used to build a toric scene.
            #------------------------------------------ Attention au decalage de 1--------------------------------
            jx = int((x[i]/dx)%grid.njx)
            jy = int((y[i]/dy)%grid.njy)
            jz = np.where(dh>z[i])[0][0]

            jz = grid.njz-jz-1 # -1 compatibilite F90-python
            print i, jx, jy, jz,x[i],y[i],z[i]
            # TO CONTINUE (line 318)
         #Cas ou il n'y avait encore rien dans la cellule (jx,jy,jz)
            if grid.kxyz[jx,jy,jz]==0 :

                 grid.kxyz[jx,jy,jz]=k+1 #ajouter 1 pour utilisation f90
                 grid.numx[k]=jx + 1 #ajouter 1 pour utilisation f90
                 grid.numy[k]=jy + 1 #ajouter 1 pour utilisation f90
                 grid.numz[k]=jz + 1 #ajouter 1 pour utilisation f90
                 grid.nje[k]=1
                 grid.nume[1,k]=entity[i]
                 grid.leafareadensity[1,k]=s[i]/(dx*dy*dz[jz])
                 grid.s_vt_vx[1,k]=s[i]
                 grid.s_vx[k]=s[i]
                 grid.n_detailed[1,k]=n[i]
                 k=k+1
            else:
              #    Cas ou il y avait deja quelque chose dans la cellule [jx,jy,jz]

                kk=grid.kxyz[jx,jy,jz]-1 #retirer 1 pour compatiblite python
                je=1
                while (grid.nume[je,kk]!= entity[i] and je<=grid.nje[kk]):
                    je=je+1

                grid.leafareadensity[je,kk]=grid.leafareadensity[je,kk]+s[i]/(dx*dy*dz[jz])

                grid.n_detailed[je,kk]=(grid.n_detailed[je,kk]*grid.s_vt_vx[je,kk]+n[i]*s[i])/(grid.s_vt_vx[je,kk]+s[i])
                grid.s_vt_vx[je,kk] = grid.s_vt_vx[je,kk] + s[i]
                grid.s_vx[kk] = grid.s_vx[kk] + s[i]
                grid.nje[kk]=max(je,grid.nje[kk])
                grid.nemax=max(grid.nemax,grid.nje[kk])
                grid.nume[je,kk]=entity[i]
        print 'i,j,k,lad,surface1,surface2,azote'
        for k in range(grid.njx* grid.njy* grid.njz):
            print grid.numx[k],grid.numy[k],grid.numz[k],grid.leafareadensity[1,k],grid.s_vt_vx[1,k], grid.s_vx[k],grid.n_detailed[1,k]


def _read(f, *args):
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l = l.strip().split(' ')
    l = filter(None,l)
    assert len(args) <= len(l)
    args = list(args)

    for i in range(len(args)):
        taille = args[i].size
        args[i].fill(l[i])
        if  taille >1:
            k=0
            for j in l[i:(i+taille)]:
                args[i][k]=np.float32(j)
                k=k+1
    return









