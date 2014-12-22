Getting Started
################

Things to know about pyRATP ...
===============================
Based on a single Fortran90 program, the OpenAlea version of RATP is still implemented 
in Fortran90 with some specificities:

- The RATP code is now divided into several Fortran90 modules which can be used as a Python library in the ALEA environment. A Fortran90 module includes public variables and subroutines, which are all accessible in the ALEA environment.
- Input variables and files are managed in Python through dedicated python nodes available in the VisuAlea environment.
- The RATP core i.e. radiation balance, heat energy balance and leaf physiological models (transpiration and photosynthesis) are still Fortran90 modules and are not available for users.
 
First tutorial
==============
 
Load pyRATP
***********
Launch the Tuto1 composite node from the pyratp package (pyratp.demo.RATPTuto1):

.. image:: Tuto1Image.png
    :width: 30%
    :align: center

The following workspace should open :

.. dataflow:: pyratp.demo RATPTuto1

This workspace is composed of:

#. Five input files (first line): from left to right: the 3D plant file, the grid configuration file, the vegetation file, the sky discretization file and the meteo data file.
#. Five nodes to read input files (second line)
#. One specific node to fill the grid with the 3D leaves (fillgrid)
#. The RATP core (do_all)

Description of input files
--------------------------
Many input parameters are necessary to run RATP. It is out of the scope of this short tutorial to describe all this parameters. All information about these input files can be found in /LINK TO PDF ou WORD FILE/  

Run pyRATP
**********
To run RATP click right on the node "do_all" and run the node. All the input files will be read sequentially. The success of each step and the computational time are highlighted in the console window as follow:  
::
  VEGE3D OK
  GRILLE OK
  GRILLE OK
  VEGETATION OK
  SKYVAULT OK
  MICROMETEO OK
  Evaluation time: 3.07400012016 

pyRATP outputs
**************
By default 4 output files are stored in the directory: C:\\tmpRATP\\Resul\\: data.txt, spatial.txt, tree.txt and VoxelsGrid.vgx.

Description of output files
---------------------------
#. The data.txt file: this ASCII file lists the values of all input parameters
#. The spatial.txt file:  this ASCII file contains all variables for each voxel and each time step. Each variable is store column by column
#. The tree.txt file: this ASCII file stores all some variables computed at the scene scale
#. The VoxelsGrid.vgx file: this is a vegeSTAR file taht enables to visualize the grid with the VegeSTAR Software (http://www6.clermont.inra.fr/piaf/Telechargements) or with PlantGL

Visualize outputs
---------------------------

TODO
#####

.. todo::
    * Loop with RATP is broken:
        - Debug deallocation and destroy functions
    * Create inputs as objects to be able to modify the parameters in memory.



