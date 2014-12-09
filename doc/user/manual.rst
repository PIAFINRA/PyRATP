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


Run pyRATP
*********** 

pyRATP outputs
**************

Description of output files
---------------------------

Visualize outputs
---------------------------

TODO
#####

.. todo::
    * Loop with RATP is broken:
        - Debug deallocation and destroy functions
    * Create inputs as objects to be able to modify the parameters in memory.



