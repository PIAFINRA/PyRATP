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
        ratp.out_time_spatial = np.zeros(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*14*pyratp.grid3d.nent).reshape(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*pyratp.grid3d.nent ,14)
        ratp.out_time_tree = np.zeros(pyratp.micrometeo.nbli*98*pyratp.grid3d.nent).reshape(pyratp.micrometeo.nbli*pyratp.grid3d.nent ,98)

        if os.path.isdir("c:/tmpRATP"):
            shutil.rmtree("c:/tmpRATP")
        #path = '/tmp/tmpRATP'
        path = 'c:/tmpRATP'
        os.mkdir("c:/tmpRATP/")
        os.mkdir(path+"/Resul")
        print np.where(pyratp.vegetation_types.ismine==1)
        try:
            numeroMin = (np.where(pyratp.vegetation_types.ismine==1))[0][0] + 1
            blMin=np.where(pyratp.grid3d.nume==numeroMin)
            if len(blMin[0])>0:
                pyratp.ratp.do_all_mine()
            else:
                pyratp.ratp.do_all()
        except:
            pyratp.ratp.do_all()





        np.savetxt('c:/spacial.txt',ratp.out_time_spatial,'%.6e')
        np.savetxt('c:/tree.txt',ratp.out_time_tree,'%.6e')