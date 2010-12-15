"""
Python macro for RATP simulation:
Need input files in the same directory:
- grid3D.PP1	: contains parameters of the 3D grid
- digital.PP1	: contains canopy geometry, as a collection of leaves
- skyvault.PP1	: contains parameters of sky discretisation (here, as a 46-direction turtle sky)
- speciesplano.spc: contains parameters of vegetation types, ie physical and biological properties
- mmeteo.PP1	: contains microclimate data, ie one line = one time step
Prefixes grid3D, digital, skyvault and mmeteo are keywords used in RATP, so that simulation is identified from the file suffix (here, PP1)
"""

import sys
#sys.path+=[r'D:\Documents and Settings\sinoquet\Herve\Datele Mele\f2py test\RatpPy_dec03']	# include in sys.path the directory containing input files and libRATP Python library 

import libRatp

SPEC="PP1"					# define a simulation by file suffix, here "PP1"

# Solution 1 : make the 3D grid from files
libRatp.grid3d.read(SPEC)		# create the empty 3D grid from parameters found in file grid3D.PP1
libRatp.grid3d.fill(SPEC,1)		# fill the 3D grid from information found in file digital.PP1

# Solution 2 : make the grid from minimum set of parameters : number of voxels along X Y Z axis, size of bounding box along X, Y Z axis
# Other parameters are given default values
# Solution 2 must be used to fill the grid from MVS module
njx = 2
njy = 3
njz = 4
size_box_x = 4.	# meters
size_box_y = 5.	# meters
size_box_z = 3.75	# meters

libRatp.grid3d.create(njx,njy,njz,size_box_x,size_box_y,size_box_z)		# create the empty 3D grid from parameters found in file grid3D.PP1

libRatp.grid3d.xlad = Extract(mvs, Scale=2, Data=leaf_area_density)		# je pense que c'est ici qu'il faut alimenter les tableaux d'entrée de structure de RATP

# A ce stade, la grille est construite ...

libRatp.skyvault.create(SPEC,1)	# create the skyvault from information found in file skyvault.PP1
libRatp.vegetation_types.create(libRatp.grid3d.nent,'speciesplano.spc')	# read vegetation parameters, here in file speciesplano.spc
"""
WARNING:
vegetation parameters are read from one file per vegetation type
here 2 vegetation types are used, with the same name given only ONCE as an argument of method create (temporary solution of demo in La Rochelle)
"""

libRatp.diffscatt_interception.do_all()	#	compute interception of incident diffuse and scattered radiation

libRatp.micrometeo.initiate(SPEC)		#	open microclimate file, ie file mmeteo.PP1
while libRatp.micrometeo.iarretmm == False:	# while the end of file mmeteo.PP1 is not reached
   libRatp.micrometeo.inputdata()			# read microclimate data of current time step
   if libRatp.micrometeo.iarretmm == False:
            libRatp.shortwave_radiation_balance.do_all()	# compute short wave radiation balance
		leaf_irradiance = libRatp.shortwave_radiation_balance.parirrad		# par exemple pour récuperer un tableau de sortie de RATP
            libRatp.energy_balance.energy_balance_do_all()	# compute energy balance

"""
WARNING:
There is presently no output module, so that computed values are not stored in files
Output data is available in public variables of the RATP modules
"""
        

# Remplissage manuel des tableaux ...

libRatp.grid3d.xlad=[[ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1., 1.,1.,1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  0.]]

libRatp.grid3d.kxyz=[[[1, 2, 3, 4, 1],[5, 6, 7, 8, 2],[9, 10, 11, 12, 3]],[[13, 14, 15, 16, 4],[17, 18, 19, 20, 5],[21, 22, 23, 24, 6]]]


libRatp.grid3d.numx=[1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]
libRatp.grid3d.numy=[1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3]
libRatp.grid3d.numy=[1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4]


