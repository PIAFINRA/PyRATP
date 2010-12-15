import sys
# include in sys.path the directory containing input files and Ratp Python library
#sys.path+=[r'C:\Python23\Lib\site-packages\Ratp']	

import alinea.pyratp.pyratp as Ratp
import Ratp
from numpy import *

# un seul type de vegetation dans le grille
nentmax = 1
# define a simulation by file suffix, here "PP1"
SPEC="PP1"					

# new
Ratp.constant_values.cv_set()

class RatpPy:
   def __init__(self,grid):

      self.grid=grid
      Ratp.constant_values.cv_set()
      
      Ratp.grid3d.nentmax = nentmax
      # RATP now have to allocate memory
      Ratp.grid3d.g3d_create(grid.nx,grid.ny,grid.nz,
                             grid.bb[0]/100.,grid.bb[1]/100.,grid.bb[2]/100.)

      Ratp.grid3d.leafareadensity= resize(grid.lad_num*10.,
                                          (Ratp.grid3d.nent,size(grid.lad_num)))
     
      Ratp.grid3d.numx= grid.voxelCoords[:,0]
      Ratp.grid3d.numy= grid.voxelCoords[:,1]
      Ratp.grid3d.numz= grid.voxelCoords[:,2]

      Ratp.grid3d.nveg= grid.nb_filled

      Ratp.grid3d.kxyz = grid.kxyz
      dx, dy, dz= Ratp.grid3d.dx, Ratp.grid3d.dy, Ratp.grid3d.dz[0]
      Ratp.grid3d.s_vt_vx= Ratp.grid3d.leafareadensity *dx*dy*dz

      Ratp.grid3d.s_vt=array([sum(Ratp.grid3d.s_vt_vx[0])])
      Ratp.grid3d.s_vx=Ratp.grid3d.s_vt_vx[0]
      Ratp.grid3d.s_canopy= Ratp.grid3d.s_vt[0]


   def create_skyvault(self):
      # create the skyvault from information found in file skyvault.PP1
      Ratp.skyvault.sv_read(SPEC)	

   def create_vegetation_type(self):
      # read vegetation parameters
      Ratp.vegetation_types.vt_read(Ratp.grid3d.nent, SPEC)	

   def nb_dirs(self):
       return size(Ratp.skyvault.hmoy)
    
   def compute_STARdir(self, i):
      # compute interception of incident diffuse and scattered radiation
     
      # Set elevation, azimuth and solid angle
      elevation = Ratp.skyvault.hmoy[i]
      azimuth = Ratp.skyvault.azmoy[i]
      solid_angle = Ratp.skyvault.omega[i]

      # Set beam spacing along X and Y axis
      dpx = Ratp.grid3d.dx / 5.				
      dpy = Ratp.grid3d.dy / 5.
      
      # No computation of exchange coefficients of scattered radiation
      Ratp.dir_interception.scattering=False
      
      # compute directional interception
      Ratp.dir_interception.di_doall(elevation,azimuth,solid_angle,dpx,dpy)
      
      #Ratp.hemi_interception.hi_doall()
      return Ratp.dir_interception.star_vx



