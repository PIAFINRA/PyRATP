# Header
#

"""

"""

from alinea.pyratp import pyratp
#import pyRATP
import numpy as np
import math
import os
pj = os.path.join

class Vegetation(object):
    """
    """
    def __init__(self, *args, **kwds):
        """
        """
        pass

    @staticmethod
    def read(filename):

        chemin=str(os.path.dirname(filename))
        vegetation = pyratp.vegetation_types
        listVegeNom = []
        f = open(filename)
        listVege = f.readlines()
        f.close()
        listParamVege=[]
        nent = len(listVege)
        vegetation.mu = np.zeros(nent)
        vegetation.nbincli = np.zeros(nent)
        vegetation.nblo = np.zeros(nent)
        vegetation.aga = np.zeros(nent*2).reshape(nent,2)
        vegetation.agsn = np.zeros((nent,2))
        vegetation.i_gspar = np.zeros(nent)
        vegetation.agspar = np.zeros((nent,10))
        vegetation.i_gsca = np.zeros(nent)
        vegetation.agsca = np.zeros((nent,10))
        vegetation.i_gslt = np.zeros(nent)
        vegetation.agslt = np.zeros((nent,10))
        vegetation.agsvpd = np.zeros((nent,3))
        vegetation.avcmaxn = np.zeros((nent,2))
        vegetation.ajmaxn = np.zeros((nent,2))
        vegetation.ardn = np.zeros((nent,2))

        vegetation.ismine = np.zeros(nent)
        vegetation.epm = np.zeros(nent)

        varTemp=np.zeros(1)
        varMine=np.zeros(1)
        varEpm=np.zeros(1)

        jent=0
        for i in listVege:
            # second column
            fn = i.split(' ')[1].strip()
            nomfVeg = pj(chemin, fn)
            fVeg = open(nomfVeg)


            _read(fVeg,varTemp)
            vegetation.mu[jent] = varTemp
            _read(fVeg,varTemp)
            vegetation.nbincli[jent]=varTemp
            if jent==0:
                vegetation.distinc =  np.zeros((nent,vegetation.nbincli[jent]))
            _read(fVeg,vegetation.distinc[jent])
            _read(fVeg,varTemp)
            vegetation.nblo[jent]=varTemp

            if jent==0:
                vegetation.nblomin = vegetation.nblo[jent]
                vegetation.rf =  np.zeros((nent,vegetation.nblo[jent]))
            _read(fVeg,vegetation.rf[jent])

            _read(fVeg,vegetation.aga[jent])
            _read(fVeg,vegetation.agsn[jent])

            gsPar=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gspar[jent]=gsPar[0]
            for n in range(len(gsPar[2:])):
                vegetation.agspar[jent][n] = gsPar[2:][n]


            gsCA=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gsca[jent]=gsCA[0]
            for n in range(len(gsCA[2:])):
                vegetation.agsca[jent][n] = gsCA[2:][n]


            gsLT=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gslt[jent]=gsLT[0]
            for n in range(len(gsLT[2:])):
                vegetation.agslt[jent][n] = gsLT[2:][n]

            _read(fVeg,vegetation.agsvpd[jent])


            _read(fVeg,vegetation.avcmaxn[jent])


            _read(fVeg,vegetation.ajmaxn[jent])

            _read(fVeg,vegetation.ardn[jent])
            _read(fVeg,varMine)
            vegetation.ismine[jent]=varMine
            _read(fVeg,varEpm)
            vegetation.epm[jent]=varEpm
            jent +=1
            fVeg.close()

        print 'VEGETATION OK'
        return vegetation

def _read(f, *args):
    l = f.readline()
    l= l.split('!')[0] # remove comments
    l = l.split('\t')
    l = filter(None,l)
    assert len(args) <= len(l)
    args = list(args)

    for i in range(len(args)):
        taille = args[i].size
        args[i].fill(l[i])
        if  taille >1:
            k=0
            for j in l[i:(i+taille)]:
                args[i][k]=np.float32(j)
                k=k+1
    return














