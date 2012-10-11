Getting Started
################

Things to know ...
------------------
Based on a single Fortran90 program, the OpenAlea version of RATP is still implemented 
in Fortran90 with some specificities:

- The RATP code is now divided into several Fortran90 modules which can be used as a Python library in the ALEA environment. A Fortran90 module includes public variables and subroutines, which are all accessible in the ALEA environment.
- Input variables and files are managed in Python through dedicated python nodes available in the VisuAlea environment.
- The RATP core i.e. radiation balance, heat energy balance and leaf physiological models (transpiration and photosynthesis) are still Fortran90 modules and are not available for users.
 
First tutorial
---------------

.. dataflow:: pyratp.demo complet2

TODO
#####

.. todo::
    * Loop with RATP is broken:
        - Debug deallocation and destroy functions
    * Create inputs as objects to be able to modify the parameters in memory.



