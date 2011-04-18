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
        print nbli
        f.close()

        f = open(filename)
        f.readline()
        li=[]
        for i in range(nbli):
            li.append(_read(f))
        tabMeteo = np.array(li)
        print tabMeteo
        print tabMeteo[1]

def _read(f):
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l= l.split('\n')[0] # remove chr(13)
    l = l.split(' ')
    l = filter(None,l)
    return l

