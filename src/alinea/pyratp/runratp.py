# Header
#

"""
"""

from alinea.pyratp import pyratp
##import vegetation
import numpy as np
import os
import shutil
import tempfile
import sys
#import pyRATP
import subprocess
class runRATP(object):
    """
    """
    def __init__(self, *args, **kwds):
        """
        """
        pass
    @staticmethod
    def DoAll(*args):
        ratp = pyratp.ratp
        ratp.out_time_spatial = np.zeros(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*10*pyratp.grid3d.nent).reshape(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*pyratp.grid3d.nent ,10)
        ratp.out_time_tree = np.zeros(pyratp.micrometeo.nbli*96*pyratp.grid3d.nent).reshape(pyratp.micrometeo.nbli*pyratp.grid3d.nent ,96)

        if os.path.isdir("c:/tmpRATP"):
            shutil.rmtree("c:/tmpRATP")
        #path = '/tmp/tmpRATP'
        path = 'c:/tmpRATP'
        os.mkdir("c:/tmpRATP/")
        os.mkdir(path+"/Resul")
##        p = subprocess.Popen('cmd.exe', stdout=subprocess.PIPE)
##        print p.communicate()
        print 'avant'
        numeroMin = (np.where(pyratp.vegetation_types.ismine==1))[0][0] + 1
        print 'apres'
##        print pyratp.grid3d.nume

        blMin=np.where(pyratp.grid3d.nume==numeroMin)
        print "pyratp.grid3d.nveg",pyratp.grid3d.nje,pyratp.grid3d.nveg
        print "numeroMin ,blMin",numeroMin ,blMin
        print "len(blMin)[0]",len(blMin[0])
        if len(blMin[0])>0:
            pyratp.ratp.do_all_mine()
        else:
            pyratp.ratp.do_all()
##        print 'ratp.out_time_spatial',ratp.out_time_spatial
##        print 'ratp.out_time_tree',ratp.out_time_tree

##        return ratp.out_time_spatial.tostring(),ratp.out_time_tree.tostring()
##        return ratp.out_time_spatial,ratp.out_time_tree
        np.savetxt('c:/spacial.txt',ratp.out_time_spatial,'%.6e')
        np.savetxt('c:/tree.txt',ratp.out_time_tree,'%.6e')