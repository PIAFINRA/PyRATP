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
        skyvault.ndir=int(f.readline().strip().split('\t')[0])
        skyvault.hmoy=np.zeros(skyvault.ndir)
        skyvault.azmoy=np.zeros(skyvault.ndir)
        skyvault.omega=np.zeros(skyvault.ndir)
        skyvault.pc=np.zeros(skyvault.ndir)
        for n in range(skyvault.ndir):
            listGene.append(f.readline().strip().split('\t'))
        tabGene=np.array(listGene)
        tabGene = np.cast['float64'](tabGene)
        skyvault.hmoy=np.transpose(tabGene)[0]*math.pi / 180
        skyvault.azmoy=np.transpose(tabGene)[1]*math.pi / 180
        skyvault.omega=np.transpose(tabGene)[2]
        skyvault.pc=np.transpose(tabGene)[3]
        print 'SKYVAULT OK'
        f.close()


