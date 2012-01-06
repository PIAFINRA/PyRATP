"""
Python macro for RATP simulation:
Need input files in the same directory:
- grid3D.PP1	: contains parameters of the 3D grid
- digital.PP1	: contains canopy geometry, as a collection of leaves
- skyvault.PP1	: contains parameters of sky discretisation (here, as a 46-direction turtle sky)
- vegetation.PP1: contains file names of vegetation parameters
- plano_walnut.veg: contains parameters of vegetation types, ie physical and biological properties
- mmeteo.PP1	: contains microclimate data, ie one line = one time step
Prefixes grid3D, digital, skyvault and mmeteo are keywords used in RATP, so that simulation is identified from the file suffix (here, PP1)
"""

#import sys
#sys.path+=[r'D:\Documents and Settings\sinoquet\Herve\Datele Mele\f2py test']	# include in sys.path the directory containing input files and Ratp Python library 

import Ratp
#Ratp.__doc__

# set values of physical constants
Ratp.constant_values.cv_set()
Ratp.constant_values.r		# Perfect gas constant
Ratp.constant_values.sigma		# Stephan-Boltzman constant


# define a simulation by file suffix, here "PP1"

SPEC="PP1"					

# Solution 1 : make the 3D grid from files
# create the empty 3D grid from parameters found in file grid3D.PP1
Ratp.grid3d.g3d_read(SPEC)	
# fill the 3D grid from information found in file digital.PP1
Ratp.grid3d.g3d_fill("PP1",1)	

# A ce stade, la grille est construite ...

# create the skyvault from parameters found in file skyvault.PP1
Ratp.skyvault.sv_read(SPEC)	
# number of vegetation types in the 3D grid.
nvt = Ratp.grid3d.nent		
# read vegetation parameters, from nvt files, the name of which is found in file vegetation.PP1.
Ratp.vegetation_types.vt_read(nvt,SPEC)	
"""
WARNING:
vegetation parameters are read from one file per vegetation type
here 2 vegetation types are used, with the same name given only ONCE as an argument of method create (temporary solution of demo in La Rochelle)
"""

# STAR computation (i.e. for a given direction)
elevation = Ratp.skyvault.hmoy[1]		# Set elevation angle
azimuth = Ratp.skyvault.azmoy[1]		# Set azimuth angle
solid_angle = Ratp.skyvault.omega[1]	# Set solid angle
dpx = Ratp.grid3d.dx / 5.				# Set beam spacing along X-axis
dpy = Ratp.grid3d.dy / 5.				# Set beam spacing along Y-axis
# No computation of exchange coefficients of scattered radiation
Ratp.dir_interception.scattering=False
# compute directional interception
Ratp.dir_interception.di_doall(elevation,azimuth,solid_angle,dpx,dpy)
Ratp.dir_interception.star_canopy		# print STAR value at canopy scale

# STARsky computation, i.e. integration of STAR on sky vault hemisphere
Ratp.hemi_interception.hi_doall()
Ratp.hemi_interception.starsky_canopy		# print sky-integrated STAR value at canopy scale


# input meteorological data
ntime=2				# integer time_step
Ratp.micrometeo.mm_read(SPEC,ntime)	# read meteo data, at data line ntime in file mmeteo.PP1


# short wave radiation balance computations
Ratp.shortwave_balance.swrb_doall()
# energy balance computations
Ratp.energy_balance.eb_doall()
# photosynthesis computations
Ratp.photosynthesis.farquhar_parameters_set()
Ratp.photosynthesis.farquhar_scaling_factors()
Ratp.photosynthesis.ps_doall()

"""
WARNING:
There is presently no output module, so that computed values are not stored in files
Output data is available in public variables of the RATP modules
"""
        

"""
# Solution 2 : make the grid from minimum set of parameters : number of voxels along X Y Z axis, size of bounding box along X, Y Z axis
# Other parameters are given default values
# Solution 2 must be used to fill the grid from MVS module
njx = 2
njy = 3
njz = 4
size_box_x = 4.	# meters
size_box_y = 5.	# meters
size_box_z = 3.75	# meters

Ratp.grid3d.create(njx,njy,njz,size_box_x,size_box_y,size_box_z)		# create the empty 3D grid from parameters found in file grid3D.PP1

Ratp.grid3d.xlad = Extract(mvs, Scale=2, Data=leaf_area_density)		# je pense que c'est ici qu'il faut alimenter les tableaux d'entrée de structure de RATP

# Ici remplissage manuel des tableaux ...

Ratp.grid3d.xlad=[[ 1., 1., 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1., 1.,1.,1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1., 1., 1.]]
Ratp.grid3d.kxyz=[[[1, 2, 3, 4, 1],[5, 6, 7, 8, 2],[9, 10, 11, 12, 3]],[[13, 14, 15, 16, 4],[17, 18, 19, 20, 5],[21, 22, 23, 24, 6]]]
Ratp.grid3d.numx=[1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]
Ratp.grid3d.numy=[1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3]
Ratp.grid3d.numz=[1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4]
Ratp.grid3d.nveg=njx*njy*njz

"""
