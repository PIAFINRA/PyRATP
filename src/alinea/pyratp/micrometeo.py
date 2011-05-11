# Header
#

"""

"""

from alinea.pyratp import pyratp
#import pyRATP
import numpy as np
import math
import os
class MicroMeteo(object):
    """
    """
    def __init__(self, *args, **kwds):
        """
        """
        pass

    @staticmethod
    def read(filename):
        chemin=str(os.path.dirname(filename))
        micrometeo = pyratp.micrometeo
        listVegeNom = []
        f = open(filename)
        nbli = len(f.readlines())-1
        micrometeo.nbli=nbli
        f.close()
        col = np.int32(13)

        micrometeo.tabmeteo = np.zeros(micrometeo.nbli*col).reshape(micrometeo.nbli ,col)

        f = open(filename)
        f.readline()
        li=[]
        for i in range(nbli):
            li=_read(f)
            for ii in range(len(li)):
                micrometeo.tabmeteo[i,ii] = li[ii]
        f.close()
        print 'MICROMETEO OK'
        return micrometeo


def _read(f):
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l= l.split('\n')[0] # remove chr(13)
    l = l.split(' ')
    l = filter(None,l)
    for j in range(len(l)):
        l[j]=np.float32(l[j])
    return l

