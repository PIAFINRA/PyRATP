# Header
#

"""

"""

from alinea.pyratp import pyratp
#import pyRATP
import numpy as np
import math
import os
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
        print listVege
        f.close()
        listParamVege=[]
        nent = len(listVege)
        vegetation.mu = np.zeros(nent)
        vegetation.nbincli = np.zeros(nent)
        vegetation.nblo = np.zeros(nent)
        vegetation.Aga = np.zeros((nent,2))
        vegetation.AgsN = np.zeros((nent,2))
        vegetation.i_gsPAR = np.zeros(nent)
        vegetation.AgsPAR = np.zeros((nent,10))
        vegetation.i_gsCA = np.zeros(nent)
        vegetation.AgsCA = np.zeros((nent,10))
        vegetation.i_gsLT = np.zeros(nent)
        vegetation.AgsLT = np.zeros((nent,10))
        vegetation.AgsVPD = np.zeros((nent,3))
        vegetation.AVcmaxN = np.zeros((nent,2))
        vegetation.AJmaxN = np.zeros((nent,2))
        vegetation.ARdN = np.zeros((nent,2))

        vegetation.Ismine = np.zeros(nent)
        vegetation.epm = np.zeros(nent)

        varTemp=np.zeros(1)
        varMine=np.zeros(1)
        varEpm=np.zeros(1)

        jent=0
        for i in listVege:
            nomfVeg = chemin + '\\'+ i.split(' ')[1][:-1]
            fVeg = open(nomfVeg)


            _read(fVeg,varTemp)
            vegetation.mu[jent] = varTemp
            print 'vegetation.mu',vegetation.mu
            _read(fVeg,varTemp)
            vegetation.nbincli[jent]=varTemp
            print 'vegetation.nbincli',vegetation.nbincli
            if jent==0:
                vegetation.distinc =  np.zeros((nent,vegetation.nbincli[jent]))
                print 'vegetation.distinc',vegetation.distinc
            _read(fVeg,vegetation.distinc[jent])
            print 'vegetation.distinc',vegetation.distinc[jent]
            _read(fVeg,varTemp)
            vegetation.nblo[jent]=varTemp
            print 'vegetation.nblo[jent]', vegetation.nblo[jent]

            if jent==0:
                vegetation.rf =  np.zeros((nent,vegetation.nblo[jent]))
            _read(fVeg,vegetation.rf[jent])
            print 'vegetation.rf[jent]',vegetation.rf[jent]

            _read(fVeg,vegetation.Aga[jent])
            _read(fVeg,vegetation.AgsN[jent])
            print 'vegetation.AgsN',vegetation.AgsN

            gsPar=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gsPAR[jent]=gsPar[0]
            for n in range(len(gsPar[2:])):
                vegetation.AgsPAR[jent][n] = gsPar[2:][n]
            print 'AgsPAR',vegetation.AgsPAR


            gsCA=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gsCA[jent]=gsCA[0]
            for n in range(len(gsCA[2:])):
                vegetation.AgsCA[jent][n] = gsCA[2:][n]
            print 'AgsCA',vegetation.AgsCA


            gsLT=(fVeg.readline().split('!')[0]).split('\t')
            vegetation.i_gsLT[jent]=gsLT[0]
            for n in range(len(gsLT[2:])):
                vegetation.AgsLT[jent][n] = gsLT[2:][n]
            print 'AgsLT',vegetation.AgsLT

            _read(fVeg,vegetation.AgsVPD[jent])
            print 'vegetation.AgsVPD',vegetation.AgsVPD

            _read(fVeg,vegetation.AVcmaxN[jent])
            print 'vegetation.AVCmaxN',vegetation.AVcmaxN

            _read(fVeg,vegetation.AJmaxN[jent])
            print 'vegetation.AJmaxN[jent]',vegetation.AJmaxN[jent]

            _read(fVeg,vegetation.ARdN[jent])
            print 'vegetation.ARdN[jent]',vegetation.ARdN[jent]
            _read(fVeg,varMine)
            vegetation.Ismine[jent]=varMine
            print 'vegetation.Ismine[jent]',vegetation.Ismine[jent]
            _read(fVeg,varEpm)
            vegetation.epm[jent]=varEpm
            print 'vegetation.epm[jent]',vegetation.epm[jent]
            jent +=1
            fVeg.close()



def _read(f, *args):
    l = f.readline()
    l= l.split('!')[0] # remove comments
##    print 'l1',l, type(l)
    l = l.strip().split('\t')
##    l = l.split('\t')
##    print 'l2',l, type(l)
    l = filter(None,l)
##    print 'l3',l, type(l)
    assert len(args) <= len(l)
    args = list(args)
##    print 'args',args, len(args)

    for i in range(len(args)):
        taille = args[i].size
        args[i].fill(l[i])
        if  taille >1:
            k=0
            for j in l[i:(i+taille)]:
                args[i][k]=np.float32(j)
                k=k+1
    return

##        for n in range(ndir):
##            nomVege.append(f.readline().strip().split('\t'))
##        tabGene=np.array(listGene)
##        tabGene = np.cast['float64'](tabGene)
##        hmoy=np.transpose(tabGene)[0]*math.pi / 180
##        azmoy=np.transpose(tabGene)[1]*math.pi / 180
##        omega=np.transpose(tabGene)[2]
##        pc=np.transpose(tabGene)[3]














