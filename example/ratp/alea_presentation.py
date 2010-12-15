
"""
   Presentation ALEA :  REA Decembre 2003
   **************************************
"""

import os
import sys
#os.chdir(r'D:\pradal\formation\Demo')
#sys.path.append(os.curdir)

######################################################
# Loading and exploring a digitized Plant with AMAPmod
######################################################

from amlPy import *

mtg= "./manguier_a21.mtg"
drf= "./manguier.drf"

import AMAPmod
lt= AMAPmod.lineTree(mtg,drf)

################################################################
# Building a multiscale voxel space for analyzing plant geometry
################################################################

VDepth = 3
grid_scale=3
divisionsteps = 3

mvs = MSVoxel(lt, DivisionSteps=[divisionsteps], Depth=VDepth)
Plot(mvs, Scale=grid_scale)

import Grid

grid= Grid.MSVoxel2Grid(mvs,grid_scale,divisionsteps)

###################
# Using RATP module
###################

# 1 Accessing primitives of lib RATP


import RatpPy

ratp= RatpPy.RatpPy(grid)

# create the skyvault from information found in file skyvault.PP1
ratp.create_skyvault()

# read vegetation parameters
ratp.create_vegetation_type()

# compute interception of incident diffuse and scattered radiation
#star= ratp.compute_STARdir(0)

#scene= grid.getRepresentation(star)

###############################################
# Using PlantGL module to explore RATP results
###############################################

from PlantGL import *

#Viewer.display(scene)

n= ratp.nb_dirs()
for i in range(2):
    r = Viewer.question("Star Visualization","Step "+str(i)+"/"+str(n))
    star= ratp.compute_STARdir(i)
    Viewer.display(grid.getRepresentation(star))




