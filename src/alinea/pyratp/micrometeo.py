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

        micrometeo.tabmeteo = np.ones(micrometeo.nbli*col).reshape(micrometeo.nbli ,col)   #17/04/2012 NGAO Set to one for HRsol default value ! 

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

    @staticmethod
    def initialise(day=1, hour=12, PARglob=1, PARdif=1, other_glob=[], other_dif=[], Ratmos=1, Tsol=1, Tair=1, Eair=1, CO2air=1, Wind=1, HRsol=1):
        """ Create a micrometeo object from data given in arguments
        
        Parameters:
        - day : day of year
        - hour : decimal hour (0-24)
        - PARglob : global (direct + diffuse) radiation in the PAR band (W.m-2)
        - PARdif : direct/diffuse ratio for PAR
        - other_glob : a list of global (direct + diffuse) radiation in the 'other than PAR' bands (W.m-2). 
        - other_dif : a list of direct/diffuse ratio for other than PAR bands.
        - Ratmos : atmospheric thermal radiation (W.m-2)
        - Tsol, Tair : soil and air temperature above the canopy (degree celcius)
        - Eair: water vapour pressure in the air (Pa)
        - CO2air: CO2 partial pressure in the air (Pa)
        - Wind: wind speed above the canopy (m.s-1)
        - HRsol: Relative Soil Humidity (0-1)
        
        """
        
        micrometeo = pyratp.micrometeo
        micrometeo.nbli = np.array(day).size # handle both list and scalar args for day
        glob = ['band' + str(i) + 'glob' for i in other_glob]
        dif = ['band' + str(i) + 'dif' for i in other_dif]
        other_bands = list(sum(zip(glob, dif),()))
        cols = ['day', 'hour', 'PARglob', 'PARdif'] + other_bands + ['Ratmos', 'Tsol', 'Tair', 'Eair', 'CO2air', 'Wind', 'HRsol']
        col = np.int32(len(cols))
        micrometeo.tabmeteo = np.ones(micrometeo.nbli*col).reshape(micrometeo.nbli ,col) 
        args = locals()
        args.update({glob[i]:other_glob[i] for i in range(len(glob))})
        args.update({dif[i]:other_dif[i] for i in range(len(dif))})
        for i,col in enumerate(cols):
            micrometeo.tabmeteo[:,i] = args[col]
        
        return micrometeo
        
def _read(f):
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l= l.split('\n')[0] # remove chr(13)
    #l = l.split(' ')
    l = l.replace('\t',' ').split(' ') 
    l = filter(None,l)
    for j in range(len(l)):
        l[j]=np.float32(l[j])
    return l

