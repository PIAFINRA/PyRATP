# Header
#

"""
"""

from alinea.pyratp import pyratp
import numpy as np
import os
import shutil
import tempfile
import sys
import grid
import subprocess
import platform

class runRATP(object):
    """
    """
    @staticmethod
    def DoAll(*args):
        ratp = pyratp.ratp
        pyratp.dir_interception.scattering = False
        ratp.out_time_spatial = np.zeros(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*20*pyratp.grid3d.nent).reshape(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*pyratp.grid3d.nent,20)
        ratp.out_time_tree = np.zeros(pyratp.micrometeo.nbli*8*pyratp.grid3d.nent).reshape(pyratp.micrometeo.nbli*pyratp.grid3d.nent ,8)
        #Ajout 1 colonne pour N foliaire, ngao 05/06/2013
        #Ajout 1 colonne pour Vegetation Type , MSaudreau 07/01/2014
        path = 'c:/tmpRATP' if platform.system() == 'Windows' else '/tmp/tmpRATP'
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        os.mkdir(path+"/Resul")
        grid.gridToVGX(pyratp.grid3d,path+"/Resul/","VoxelsGrid.vgx") #Save grid in VGX format
        ##print np.where(pyratp.vegetation_types.ismine==1)
        try:
            numeroMin = (np.where(pyratp.vegetation_types.ismine==1))[0][0] + 1
            blMin=np.where(pyratp.grid3d.nume==numeroMin)
            if len(blMin[0])>0:
                pyratp.ratp.do_all_mine()
            else:
                pyratp.ratp.do_all()
        except:
            pyratp.ratp.do_all()

        #print 'dz,', pyratp.grid3d.dz
        fspatial = open(path+"/Resul"+'/spatial.txt','w')
        fspatial.write('VegetationType  ntime  day   hour  AirTemperature  VoxelId  ShadedTemp  SunlitTemp  VoxelTemp  STARDirect STARSky ShadedPhoto SunlitPhoto  ShadedTranspi SunlitTranspi')
        fspatial.write('  ShadedArea SunlitArea ShadedGs  SunlitGs  VoxelNitrogen')
        fspatial.write('\n')
        np.savetxt(fspatial,ratp.out_time_spatial,'%.6e')
        fspatial.close()
        ftree = open(path+"/Resul"+'/tree.txt','w')
        ftree.write('ntime  day   hour  VegetationType  TotalIrradiation  AirTemperature  TreePhotosynthesis  TreeTranspiration')
        ftree.write('\n')
        np.savetxt(ftree,ratp.out_time_tree,'%.6e')
        ftree.close()

        # Ecriture parametres calcul_
        fichier = open(path+"/Resul"+"/data.txt", "a")
        #ecriture des variable grille
        fichier.write("GRILLE")
        fichier.write('\n')
        for d in pyratp.grid3d.__dict__:
            fichier.write(str(d))
            fichier.write("\t" + str(pyratp.grid3d.__dict__[d]))
            fichier.write('\n')
        fichier.write('dz'+'\t')
        for i in pyratp.grid3d.dz:
            fichier.write(str(i) + ' ')
        fichier.write('\n')

        fichier.write("VEGETATION")
        fichier.write('\n')
        vegetation = pyratp.vegetation_types
        for jent in range(pyratp.grid3d.nent):
            fichier.write('jent'+"\t")
            fichier.write(str(jent))
            fichier.write('\n')
            fichier.write('mu'+"\t")
            fichier.write(str(vegetation.mu[jent]))
            fichier.write('\n')
            fichier.write('nbincli'+"\t")
            fichier.write(str(vegetation.nbincli[jent]))
            fichier.write('\n')
            fichier.write('distinc'+"\t")
            fichier.write(str(vegetation.distinc ))
            fichier.write('\n')
            fichier.write('nblo'+"\t")
            fichier.write(str(vegetation.nblo[jent]))
            fichier.write('\n')
            fichier.write('nblomin'+"\t")
            fichier.write(str(vegetation.nblomin))
            fichier.write('\n')
            fichier.write('rf'+"\t")
            fichier.write(str(vegetation.rf ))
            fichier.write('\n')
            fichier.write('i_gspar'+"\t")
            fichier.write(str(vegetation.i_gspar[jent]))
            fichier.write('\n')
            fichier.write('agspar'+"\t")
            fichier.write(str(vegetation.agspar[jent]))
            fichier.write('\n')
            fichier.write('i_gsca'+"\t")
            fichier.write(str(vegetation.i_gsca[jent]))
            fichier.write('\n')
            fichier.write('agsca'+"\t")
            fichier.write(str(vegetation.agsca[jent] ))
            fichier.write('\n')
            fichier.write('i_gslt'+"\t")
            fichier.write(str(vegetation.i_gslt[jent]))
            fichier.write('\n')
            fichier.write('agslt'+"\t")
            fichier.write(str(vegetation.agslt[jent]))
            fichier.write('\n')
            fichier.write('agsvpd'+"\t")
            fichier.write(str(vegetation.agsvpd[jent]))
            fichier.write('\n')
            fichier.write('avcmaxn'+"\t")
            fichier.write(str(vegetation.avcmaxn[jent]))
            fichier.write('\n')
            fichier.write('ajmaxn'+"\t")
            fichier.write(str(vegetation.ajmaxn[jent]))
            fichier.write('\n')
            fichier.write('ardn'+"\t")
            fichier.write(str(vegetation.ardn[jent]))
            fichier.write('\n')
            fichier.write('ismine'+"\t")
            fichier.write(str(vegetation.ismine[jent]))
            fichier.write('\n')
            fichier.write('epm'+"\t")
            fichier.write(str(vegetation.epm[jent]))
            fichier.write('\n')


        fichier.close()

        return ratp.out_time_spatial, ratp.out_time_tree

    @staticmethod
    def DoIrradiation(*args):
        ratp = pyratp.ratp
        ratp.out_rayt = np.zeros(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*9*pyratp.grid3d.nent).reshape(pyratp.micrometeo.nbli*pyratp.grid3d.nveg*pyratp.grid3d.nent ,9)

        path = 'c:/tmpRATP' if platform.system() == 'Windows' else '/tmp/tmpRATP'
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        os.mkdir(path+"/ResulIrradiation")
        pyratp.ratp.do_interception()

        fspatial = open(path+"/ResulIrradiation"+'/spatial.txt','w')
        fspatial.write('VegetationType  Iteration day hour  VoxelId ShadedPAR SunlitPAR ShadedArea  SunlitArea')
        fspatial.write('\n')
        np.savetxt(fspatial,ratp.out_rayt,'%.6e')
        fspatial.close()



        PAR0 = np.transpose(ratp.out_rayt)[5]
        PAR1 = np.transpose(ratp.out_rayt)[6]
        #print PAR0
        #print PAR1

        # homogenizing the output matrix to get same shape as doall - Problem should be solved by changing the fortran source code.
##        rr = ratp.out_rayt.T[1:]
##        rr2 = rr.T
##        return rr2
        return ratp.out_rayt
