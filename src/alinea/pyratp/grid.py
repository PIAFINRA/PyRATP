# Header
#

"""

"""

from alinea.pyratp import pyratp
#import pyRATP
import numpy as np
import vege3D
import scipy.io as io
from openalea.plantgl import all as pgl
from math import ceil



def scenetogrid(scene, dx=0.2, dy=0.2, dz=0.2 , domain=None):
    """
    Convert a PlantGL scene to ratp grid that fit the scene
    """

    def _is_iterable(x):
        try:
            x = iter(x)
        except TypeError:
            return False
        return True

    tesselator = pgl.Tesselator()
    bbc = pgl.BBoxComputer(tesselator)
    bbc.process(scene)
    bbox = bbc.result


    xorig = bbox.getXMin()
    yorig = bbox.getYMin()
    zorig = dz

    htop = bbox.getZMax()

    nbz = int(ceil(htop / float(dz)))
    nbx = int(ceil(bbox.getXRange() / float(dx)))
    nby = int(ceil(bbox.getYRange() / float(dy)))

    return nbx, nby, nbz, dx, dy, [dz] * nbz, xorig, yorig, zorig




class Grid(object):
    """
    """
    def __init__(self, *args, **kwds):
        """

        """
    @staticmethod
    def initialise(njx, njy, njz, dx, dy, dz, xorig, yorig, zorig, latitude, longitude, timezone, nent, rs, orientation = 0, idecaly=0):
        """ Initialize the 3D grid from input arguments

        Input:Parameters:
            - number of voxels according to the three axis: njx,njy,njz
            - grid size along the three axis: dx,dy,dz
            - grid origin: xorig, yorig, zorig
            - location of the scene: latitude and longitude
            - local time: timezone
            - number of entities in the scene: nent
            - soil reflectance for PAR and NIR wavebands: rs

        Output:Parameters:
            - grid3d: object grid updated (size, number of voxels)
        """

        grid3d = pyratp.grid3d
        grid3d.njx, grid3d.njy, grid3d.njz = int(njx),int(njy),int(njz)

        #allocated to (njz+1) as needed in beampath
        grid3d.dz = np.zeros(grid3d.njz+1)

        # voxel size according to X- Y- and Z- axis
        # TEST
        grid3d.dx, grid3d.dy, grid3d.dz[:-1] = dx, dy, np.array(dz, dtype=np.float)
        # 3D grid origin
        grid3d.xorig, grid3d.yorig, grid3d.zorig = xorig, yorig, zorig

        grid3d.latitude, grid3d.longitude, grid3d.timezone = latitude, longitude, timezone

        # angle (degree) between axis X+ and North
        grid3d.orientation = orientation

        # offset between canopy units along Y-axis
        #      idecaly <> 0 : plantation en quinconce partiel (ie, decalage des Y
        #      d'un nombre entier idecaly de cellules Y d'une maille a l'autre).
        #             si idecaly = njy / 2 : quinconce parfait
        #             si idecaly = 0       : plantation orthogonale
        #      Cf. Subroutine Beampath
        idecaly = grid3d.idecaly

        # nent: number of vegetation types in the 3D grid
        grid3d.nent = nent

        # number of wavelength bands for the soil surface
        grid3d.nblosoil = int(len(rs))
        grid3d.rs = np.array(rs, dtype=np.float)


        # definition of aliases

        initParam(grid3d)

        return grid3d

    @staticmethod
    def read(filename):
        """ Creating the 3D grid from input file *.grd

        Input:Parameters:
            - a grid file ! *.grd

        Output:Parameters:
            - grid3d: object grid updated (size, number of voxels)
        """

        grid3d = pyratp.grid3d
        f = open(filename)

        # number of grid voxels along X Y and Z axis
        _read(f, grid3d.njx, grid3d.njy, grid3d.njz)

        #allocated to (njz+1) as needed in beampath
        grid3d.dz = np.zeros(grid3d.njz+1)

        # voxel size according to X- Y- and Z- axis
        # TEST
        _read(f, grid3d.dx, grid3d.dy, grid3d.dz[:-1])
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

        initParam(grid3d)

        return grid3d

##    @staticmethod

    @staticmethod
    def readVgx(filename):
        """ Reading the foliage distribution.

        Input:Parameters:
            - a VegeSTAR file

        Output:Parameters:
            - v: array of vegetation type (integer)
            - x,y,z: arrays of 3D coordinates in m (real)
            - s: array of leaf area in m2 (real)
            - n: array of nitrogen content in g/m2    (real)
        """

        v,x,y,z,s,n = vege3D.Vege3D.readVGX(filename,2)
##        print 'alen(x)',np.alen(x)
        return v,x/100,y/100,-z/100,s/10000.,n


    @staticmethod
    def fill(entity, x, y, z, s, n ,grid):
        """ Filling the 3D Grid with points, area and nitrogen content.
        Input::Parameters:
            - entity: array of vegettion type (integer)
            - x,y,z: arrays of 3D coordinates in m (real)
            - s: array of leaf area in m2 (real)
            - n: array of nitrogen content in g/m2    (real)
            - grid: object grid (see readgrid method)

        Output:Parameters:
            - grid: object grid updated (i.e. filled with leaves)
            - D_E2V: connectivity table Leaf -> Voxel
        """

#        print 'type grid', type(grid)
        if type(grid)is not(str):

            initParam(grid)

            x = x - grid.xorig
            y = y - grid.yorig
            z = z + grid.zorig
            s = s
            if z.min() < 0.:
                    print 'Some elements have a negative Z value and will be removed ...'
                    print '... change the grid size or the leaves coodinates to get all leaves within the grid'
            lneg=np.where(z<0) #suppression de feuilles ayant un z<0
##            print 'lneg',lneg
            entity=np.delete(entity,lneg[0])
            x=np.delete(x,lneg[0])
            y=np.delete(y,lneg[0])
            z=np.delete(z,lneg[0])
            s=np.delete(s,lneg[0])
            n=np.delete(n,lneg[0])



            if entity.max() >  grid.nent:
                raise ValueError('Number of entity is too great')

            if s.min() < 0.:
                raise ValueError('Negative area value is prohibited')

            ztot = grid.dz.sum()
            if z.max() > ztot:
                raise ValueError('Some Z points are outside of the grid')

            grid.nemax = 1
            k = 0

            grid.n_canopy = (n*s).sum()
            grid.s_canopy = s.sum()
             # sum the surface of each element of the same entity
            for i in range(grid.nent):
                grid.s_vt[i] = s[entity==i].sum()

            dx, dy , dz = grid.dx, grid.dy, grid.dz
            #dh: tableau des hauteurs z
            dh = np.array(0)
            for i in range(np.alen(dz)):
                dh=np.append(dh,dz[:i].sum())
            dh=np.delete(dh,0)

            #Relation Voxel2entite
            d_E2V = {} #entity id to voxel id
##            print 'np.alen(x)', np.alen(x)
            for i in range(np.alen(x)):

              # Compute the coord of each element in the grid.
                # modulo is used to build a toric scene.
                #------------------------------------------ Attention au decalage de 1--------------------------------

                jx = int((abs(x[i])/dx))
                jx=(jx)%grid.njx
                #if x[i]<=0:jx = grid.njx-jx-1  #Enleve recalage feuille dans la scene si feuille a l'exterieure

                jy = int(abs(y[i])/dy)
                jy=(jy)%grid.njy
                #if y[i]<=0:jy = grid.njy-jy-1      #Enleve recalage feuille dans la scene si feuille a l'exterieure

                jz = np.where(dh>z[i])[0][0]
                jz = grid.njz-jz+1

                # TO CONTINUE (line 318)
             #Cas ou il n'y avait encore rien dans la cellule (jx,jy,jz)
                if grid.kxyz[jx,jy,jz]==0 :
                     grid.kxyz[jx,jy,jz]=k+1 #ajouter 1 pour utilisation f90
                     grid.numx[k]=jx + 1 #ajouter 1 pour utilisation f90
                     grid.numy[k]=jy + 1 #ajouter 1 pour utilisation f90
                     grid.numz[k]=jz + 1 #ajouter 1 pour utilisation f90
                     grid.nje[k]=1
                     grid.nume[0,k]=entity[i]+1

                     grid.leafareadensity[0,k]=s[i]/(dx*dy*dz[jz])
                     grid.s_vt_vx[0,k]=s[i]
                     grid.s_vx[k]=s[i]
                     grid.n_detailed[0,k]=n[i]
                     d_E2V[str(i)] = float(k)
##                     d_E2V[i] = k

                     k=k+1
                else:
                  #    Cas ou il y avait deja quelque chose dans la cellule [jx,jy,jz]

                    kk=grid.kxyz[jx,jy,jz]-1 #retirer 1 pour compatiblite python
                    je=0
                    while (grid.nume[je,kk]!= (entity[i]+1) and (je+1)<=grid.nje[kk]):
                        je=je+1

                    grid.leafareadensity[je,kk]=grid.leafareadensity[je,kk]+s[i]/(dx*dy*dz[jz])

                    grid.n_detailed[je,kk]=(grid.n_detailed[je,kk]*grid.s_vt_vx[je,kk]+n[i]*s[i])/(grid.s_vt_vx[je,kk]+s[i])
    ##                grid.toto[je,kk]=(grid.n_detailed[je,kk]*grid.s_vt_vx[je,kk]+n[i]*s[i])/(grid.s_vt_vx[je,kk]+s[i])
                    grid.s_vt_vx[je,kk] = grid.s_vt_vx[je,kk] + s[i]
                    grid.s_vx[kk] = grid.s_vx[kk] + s[i]
                    grid.nje[kk]=max(je+1,grid.nje[kk])
                    grid.nemax=max(grid.nemax,grid.nje[kk])
                    grid.nume[je,kk]=entity[i]+1
                    d_E2V[str(i)] = float(kk)
##                    d_E2V[i] = kk


            grid.nveg=k
            grid.nsol=grid.njx*grid.njy   # Numbering soil surface areas
            for jx in range(grid.njx):
                for jy in range(grid.njy):
                    grid.kxyz[jx,jy,grid.njz]=grid.njy*jx+jy+1
            grid.n_canopy=grid.n_canopy/grid.s_canopy

            for k in range(grid.nveg):
                for je in range(grid.nje[k]):
                    if je==0:
                     grid.volume_canopy[grid.nent]=grid.volume_canopy[grid.nent]+dx*dy*dz[grid.numz[k]-1]  # Incrementing total canopy volume
                    if  grid.s_vt_vx[je,k]> 0. :
                     grid.volume_canopy[grid.nume[je,k]-1]=grid.volume_canopy[grid.nume[je,k]-1]+dx*dy*dz[grid.numz[k]-1]
                     grid.voxel_canopy[grid.nume[je,k]-1]=grid.voxel_canopy[grid.nume[je,k]-1]+1


##            _savegrid(grid,d_E2V,"c:/matGridRATP_Strasbourg.mat") #appel de la procedure savegrid (voir plus bas)
            gridToVGX(grid,"C:/Users/msaudreau/Desktop/Weiwei_Work/","gridVGX.vgx") #Save grid in VGX format

            return grid, d_E2V

        else:
            #gridToVGX(grid,"c:/","gridVGX.vgx") #Save grid in VGX format
           return grid, d_E2V #_importgrid(grid)

def initParam(grid3d):
##        print 'GRILLE OK debut'
        njx, njy, njz = grid3d.njx, grid3d.njy, grid3d.njz
        dx, dy = grid3d.dx, grid3d.dy
##        kxyz = grid3d.kxyz

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
##        grid3d.toto = np.zeros(nent*nvegmax).reshape(nent, nvegmax)
        grid3d.nume = np.zeros(nent*nvegmax).reshape(nent, nvegmax)

        # Leaf area (m^2) per voxel and vegetation type
        grid3d.s_vt_vx =  np.zeros(nent*nvegmax).reshape(nent, nvegmax)
        # Leaf area (m^2) per voxel
        grid3d.s_vx = np.zeros(nvegmax)
        # Leaf area (m^2) per vegetation type
        grid3d.s_vt = np.zeros(nent)

        grid3d.volume_canopy = np.zeros(nent+1)
        grid3d.voxel_canopy = np.zeros(nent)

        grid3d.int_isolated_box = 1
        grid3d.int_scattering = 0
        print 'GRILLE OK'


def gridToVGX(grid,path,filename):

    echX= grid.dx *100
    echY= grid.dy *100
    filename = path + filename
     ## VoxelsStrasbourg.vgx
    fichier = open( filename,"w")
    fichier.write( "Obj\tEchX\tEchY\tEchZ\tTransX\tTransY\tTransZ\tRotX\tRotY\tRotZ\tR\tG\tB\tnumero")
    fichier.write("\n")

    for k in range(0,grid.nveg):
        dh=grid.dz[(grid.numz[k]):].sum()
        transX = (grid.numx[k]-1)*grid.dx*100
        transY = (grid.numy[k]-0.5)*grid.dy*100
        transZ = -(grid.dz[grid.numz[k]]*0.5+dh)*100
        echZ= grid.dz[grid.numz[k]]*100
        fichier.write("35\t"+str(echX) +"\t"+ str(echY)+"\t"+str(echZ)+"\t"+str(transX)+"\t"+str(transY)+"\t"+str(transZ)+"\t0\t0\t0"+"\t0\t255\t0"+"\t"+str(k))
        fichier.write("\n")
    print "Write Grid to VGX file"
    fichier.close()



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




def _savegrid(grid,d_E2V,filename):
    ## Sauvegarde grille format MATLAB /// WE HAVE TO FIND ANOTHER WAY TO STORE THE GRID !! MS 01/2015
    dictgrid ={}                            #def d un dictionnaire dictgrid (necessaire pour io.savemat, voir plus bas)
    for i in dir(grid):
        if i<>'g3d_destroy':              #evite g3d_destroy: element de l objet grid, mais une procedure donc pas ecrivable dans un fichier .mat (voir plus bas)
            dictgrid[i] =  grid.__dict__[i] #boucle et ecrit les attributs type float
    dictgrid["dz"] =grid.dz # ajout sequentiel des differents array et nd_array (obligation de lister manuellement) au dico dictgrid
    dictgrid["s_vt_vx"] =grid.s_vt_vx
    dictgrid["s_vx"] =grid.s_vx#
    dictgrid["s_vt"] =grid.s_vt
    dictgrid["volume_canopy"] =grid.volume_canopy#
    dictgrid["voxel_canopy"] =grid.voxel_canopy
    dictgrid["kxyz"] =grid.kxyz
    dictgrid["numx"] =grid.numx#
    dictgrid["numy"] =grid.numy#
    dictgrid["numz"] =grid.numz#
    dictgrid["nje"] = grid.nje
    dictgrid["leafareadensity"] =grid.leafareadensity
    dictgrid["n_detailed"] =grid.n_detailed
    dictgrid["rs"] =grid.rs
    dictgrid["nume"] =grid.nume


#    io.savemat(filename, dictgrid,oned_as ='row') #sauvegarde du dictionnaire dictgrid, dans un fichier MATLAB: permet de inclure des float et nd_array (

#    io.savemat("C:\dE2V_Strasbourg.mat", d_E2V,oned_as ='row') #sauvegarde du dictionnaire dictgrid, dans un fichier MATLAB: permet de inclure des float et nd_array (

   # b = io.loadmat(filename)       #avantage: permet de rappeler le fichier entier

def _importgrid(filename):

    grid = pyratp.grid3d
    gridmat = io.loadmat(filename)

    grid.njx = gridmat["njx"][0]
    grid.njy = gridmat["njy"][0]
    grid.njz = gridmat["njz"][0]
    grid.dx = gridmat["dx"][0]
    grid.dy = gridmat["dy"][0]
    grid.nent = gridmat["nent"][0]


    initParam(grid)
    grid.rs = gridmat["rs"][0]
    grid.nume = gridmat["nume"]
    grid.total_ground_area = gridmat["total_ground_area"][0]
    grid.orientation = gridmat["orientation"][0]
    grid.nje = gridmat["nje"][0]
    grid.kxyz = gridmat["kxyz"]
    grid.int_scattering = gridmat["int_scattering"]
    grid.s_vx = gridmat["s_vx"][0]
    grid.timezone = gridmat["timezone"][0]
    grid.s_vt = gridmat["s_vt"][0]
    grid.n_detailed = gridmat["n_detailed"]
    grid.volume_canopy = gridmat["volume_canopy"][0]
    grid.scattering = gridmat["scattering"][0]
    grid.spec_gfill = gridmat["spec_gfill"]
    grid.latitude = gridmat["latitude"][0]
    grid.idecaly = gridmat["idecaly"][0]
    grid.n_canopy = gridmat["n_canopy"][0]
    grid.nemax = gridmat["nemax"][0]
    grid.zorig = gridmat["zorig"][0]
    grid.nblosoil = gridmat["nblosoil"][0]
    grid.numx = gridmat["numx"][0]
    grid.spec_grid = gridmat["spec_grid"]
    grid.numz = gridmat["numz"][0]
    grid.numy = gridmat["numy"][0]
    grid.nveg = gridmat["nveg"][0]
    grid.leafareadensity = gridmat["leafareadensity"]
    grid.voxel_canopy = gridmat["voxel_canopy"][0]
    grid.dz = gridmat["dz"][0]
    grid.yorig = gridmat["yorig"][0]
    grid.s_canopy = gridmat["s_canopy"][0]
    grid.isolated_box = gridmat["isolated_box"][0]
    grid.nsol = gridmat["nsol"][0]
    grid.s_vt_vx = gridmat["s_vt_vx"]
    grid.longitude = gridmat["longitude"][0]
    grid.xorig = gridmat["xorig"][0]
    grid.int_isolated_box = gridmat["int_isolated_box"][0]
    d_E2Vmat = io.loadmat("C:\dE2V_Strasbourg.mat")
    del d_E2Vmat['__version__']
    del d_E2Vmat['__globals__']
    del d_E2Vmat['__header__']
##    d_E2Vmat={}


    return grid,d_E2Vmat





