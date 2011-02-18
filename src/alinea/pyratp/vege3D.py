# Header
#

"""

"""
# Verifi? avec lecture de fichier vgx le 28/01/2011 MS certified
##from alinea.pyratp import pyratp

from PyQt4 import QtCore, QtGui
import random
#import pyRATP
import numpy as np
dicoMotCle = {}
dicoMotCle["Obj"] = 0
dicoMotCle["EchX"] = 0
dicoMotCle["EchY"] = 0
dicoMotCle["EchZ"] = 0
dicoMotCle["TransX"] = 0
dicoMotCle["TransY"] = 0
dicoMotCle["TransZ"] = 0
dicoMotCle["RotX"] = 0
dicoMotCle["RotY"] = 0
dicoMotCle["RotZ"] = 0
dicoMotCle["X1"] = 0
dicoMotCle["X2"] = 0
dicoMotCle["X3"] = 0
dicoMotCle["Y1"] = 0
dicoMotCle["Y2"] = 0
dicoMotCle["Y3"] = 0
dicoMotCle["Z1"] = 0
dicoMotCle["Z2"] = 0
dicoMotCle["Z3"] = 0
dicoMotCle["R"] = 0
dicoMotCle["G"] = 0
dicoMotCle["B"] = 0
dicoMotCle["VCmax"] = 0
#'dicoMotCle["Vcmax"] = 0
dicoMotCle["Jmax"] = 0
dicoMotCle["Resp"] = 0
dicoMotCle["Pmax"] = 0
dicoMotCle["Alpha"] = 0
dicoMotCle["Teta"] = 0
dicoMotCle["Grp1"] = 0
dicoMotCle["Grp2"] = 0
dicoMotCle["Mask"] = 0
def dicoInit():
    for k in dicoMotCle.keys():
        dicoMotCle[k] = 0

class Vege3D(object):
    """
    """
    def __init__(self, *args, **kwds):
        """

        """
    @staticmethod

    def readVGX(fileNameVGX,typeVege=1,bltypeVege=True,Azote=2):
##    def readVGX(self,fileNameVGX,typeVege=1,bltypeVege=True,Azote=2):
        nbLigne = 0
        """ Reading a VegeSTAR (*.vgx) file and return 6 numpy arrays (type of vegetation, X, Y, Z, Leaf surface and Nitrogen """
        #liste ? retourner
        tabTypeVege = np.array([])
        tabX =np.array([])
        tabY =np.array([])
        tabZ =np.array([])
        tabS =np.array([])
        tabN =np.array([])

        #lecture du fichier source
        file = QtCore.QFile(fileNameVGX)
        if not(file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
            return
        textStream = QtCore.QTextStream (file)

        #recuperation de l'entete du fichier
        if not(textStream.atEnd()):
            entete = textStream.readLine()
        #a partir de l'entete, on recupere le numero de la colonne correspondant a chaque mot cle
        #- recherche du caractere de separation
        chrSeparation = ""
        for c in entete:
            if not (str(c).isalnum()):
                chrSeparation = str(c)
                break

        #- decoupage de la ligne d'entete
        listEntete = entete.split(chrSeparation)
        #- pour chaque mot cle, on verifie qu'il existe dans le dictionaire et on note son numero de colonne
        for mot in listEntete:
            if dicoMotCle.has_key(str(mot)):
                dicoMotCle[str(mot)] = listEntete.indexOf(str(mot))+1
        nbObj=1
        listEntete = list(listEntete)

        while not(textStream.atEnd()):
            nbLigne +=1
            ligne = textStream.readLine().split(chrSeparation)

            nbObj += 1
            #transformation de la QStringList en liste python
            liste = []

            for ch in ligne :
                val=ch.toDouble() #retourne (valeur,bool)
                if not(val[1]):
                    print ch,  " : valeur non numerique a la ligne : ", nbObj+1
                    return
                liste.append(val[0])
            if bltypeVege :
                typeV = nbLigne
            else:
                typeV=random.randint(1,typeVege)

            X = (liste[listEntete.index("TransX")])
            Y = (liste[listEntete.index("TransY")])
            Z = (liste[listEntete.index("TransZ")])

            tabTypeVege= np.append(tabTypeVege,typeV)
            tabX= np.append(tabX,X)
            tabY= np.append(tabY,Y)
            tabZ= np.append(tabZ,Z)
            AREA = (liste[listEntete.index("EchX")])*(liste[listEntete.index("EchY")])*0.7
            tabS= np.append(tabS,AREA)
            tabN= np.append(tabN,Azote)

            if nbLigne == typeVege : nbLigne=0
        file.close()
        return (tabTypeVege,tabX,tabY,tabZ,tabS,tabN)



##if __name__ == "__main__":
##
##    sys.exit(app.exec_())