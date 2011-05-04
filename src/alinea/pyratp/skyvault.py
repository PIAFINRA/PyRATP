# Header
#

"""

"""

from alinea.pyratp import pyratp

#import pyRATP
import numpy as np
import math
class Skyvault(object):
    """
    """
    def __init__(self, *args, **kwds):
        """
        """
        pass

    @staticmethod
    def read(filename):
        skyvault = pyratp.skyvault
        listGene = []
        f = open(filename)
        ndir=int(f.readline().strip().split('\t')[0])
        for n in range(ndir):
            listGene.append(f.readline().strip().split('\t'))
        tabGene=np.array(listGene)
        tabGene = np.cast['float64'](tabGene)
        hmoy=np.transpose(tabGene)[0]*math.pi / 180
        azmoy=np.transpose(tabGene)[1]*math.pi / 180
        omega=np.transpose(tabGene)[2]
        pc=np.transpose(tabGene)[3]
        print 'SKYVAULT OK'
        f.close()


