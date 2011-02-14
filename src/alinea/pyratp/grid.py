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
        return grid3d

    @staticmethod
    def readVgx(filename):
        """ Filling the 3D Grid with points, area and nitrogen content.

        :Parameters:
            - `x`: an array of abscisse.
            - .
        """
        tv,tx,ty,tz,ts,tn = vege3D.Vege3D.readVGX(filename)
        print ty[5]

    @staticmethod
    def toto(entity, x, y, z, s, n):
        print 'entity',entity
        print 'x',x
        print 'y',y
        print 'z',z
        print 's',s
        print 'n',n



    @staticmethod
    def fill(entity, x, y, z, s, n):
        """ Filling the 3D Grid with points, area and nitrogen content.
        lkjfkjrzelkrjzelrkjzer
        :Parameters:
            - `x`: an array of abscisse.
            - .
        """
        print "x",x
        print entity.max()
        if entity.max() >  grid3d.nent:
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

        nft = np.alen(entity)
        grid3d.n_canopy = (n*s).sum()
        grid3d.s_canopy = s.sum()
         # sum the surface of each element of the same entity
        for i in range(grid3d.nent):
            grid3d.s_vt[i] = s[entity==i].sum()

        dx, dy = grid3d.dx, grid3d.dy

        zzz = grid3d.dz.cumsum()

        #dh: tableau des hauteurs z
        dh = np.array(0)
        for i in range(np.alen(dz)):
            dh=np.append(dh,dz[:i].sum())
        nb.delete(dh,0)

        for i in range(np.alen(x)):
            x[i] = x[i]/100 - grid3d.xorigin
            y[i] = y[i]/100 - grid3d.yorigin
            z[i] = -z[i]/100 + grid3d.zorigin

            if z[i].min() < 0.:
                raise ValueError('Some elements have a negative Z value.')


            # Compute the coord of each element in the grid.
            # modulo is used to build a toric scene.
            #------------------------------------------ Attention au decalage de 1--------------------------------
            jx = int((x[i]/dx)%njx)+1
            jy = int((y[i]/dy)%njy)+1
            jz = np.alen(np.where(dh<z[i])[0])-1
            jz = grid3d.njz-jz+1

            # TO CONTINUE (line 318)
         #Cas ou il n'y avait encore rien dans la cellule (jx,jy,jz)
##            if grid3d.kxyz(jx,jy,jz)==0 :
##                 k=k+1
##                 grid3d.kxyz(jx,jy,jz)=k
##                 grid3d.numx(k)=jx
##                 grid3d.numy(k)=jy
##                 grid3d.numz(k)=jz
##                 grid3d.nje(k)=1
##                 grid3d.nume(1,k)=jent
##                 grid3d.leafareadensity(1,k)=s/(dx*dy*dz(jz))
##                 grid3d.S_vt_vx(1,k)=s
##                 grid3d.S_vx(k)=s
##                 grid3d.N_detailed(1,k)=azot
##            else:
##              #    Cas ou il y avait deja quelque chose dans la cellule (jx,jy,jz)
##              pass
##                 kk=grid3d.kxyz(jx,jy,jz)
##                 je=1
####                 do while ((nume(je,kk).ne.jent).and.(je.le.nje(kk)))
##                while (nume(je,kk)!= jent and je<=nje(kk)):
##
##                  je=je+1
##                 end do
##
##                   leafareadensity(je,kk)=leafareadensity(je,kk)+s/(dx*dy*dz(jz))
##                 N_detailed(je,kk)=(N_detailed(je,kk)*S_vt_vx(je,kk)+azot*s)/(S_vt_vx(je,kk)+s)
##                 S_vt_vx(je,kk) = S_vt_vx(je,kk) + s
##                 S_vx(kk) = S_vx(kk) + s
##                 nje(kk)=max(je,nje(kk))
##                 nemax=max(nemax,nje(kk))
##                 nume(je,kk)=jent
##                endif
##               end if
##              end do   ! End of file
##              998 continue
##  close (2)

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
