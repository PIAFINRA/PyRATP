import numpy as np

def ExtractLight(d_e2v, data, day, hour,col):
    '''    Extract a variable from RATP output for a given date (day and hour)
    and attached this extracted variable to leaves for 3D visualization.
        Input::Parameters:
            - d_e2v: connectivity table Leaf -> Voxel (list)
            - data: a 2D array(real)
            - day, hour: time to extract data
            - col: column corresponding to data to be extracted.

        Output:Parameters:
            - extractedvar: extracted data. One data per leaf
    '''
    ls_id = [1,2]
    ls_vals = [day, hour]
    dat = extract_list(data, ls_id, ls_vals)
    dat = t_list(dat)


    extractedvar = []

    nmax = np.alen(d_e2v)

    for i in range(nmax): #Enleve nmax+1 MARC 10 12 2014
        try :
            extractedvar.append(dat[col][int(d_e2v[str(i)])])
        except:
            extractedvar.append(0)#!!! Recupere pas toutes les entites dans d_e2v!!? : A cause de triangles en z negatif!

    return extractedvar

def ExtractVoxels(data, day, hour,col):
    '''    Extract a variable from RATP output for a given date (day and hour)
    and attached this extracted variable to voxels for 3D visualization.
        Input:
            - data: a 2D array(real)
            - day, hour: time to extract data
            - col: column corresponding to data to be extracted.

        Output:
            - extractedvar: extracted data. One data per Voxel
    '''
    ls_id = [1,2]
    ls_vals = [day, hour]
    dat = extract_list(data, ls_id, ls_vals)
    dat = t_list(dat)
    nmax = len(dat[col])
    extractedvar = []
    for i in range(nmax+1):
        try :
            extractedvar.append(dat[col][i])
        except:
            extractedvar.append(0)


    return extractedvar



#!!! Recupere pas toutes les entites dans d_e2v!!?
def extract_list(dat, ls_id, ls_vals):
    """ extrait avec un ET les lignes pour les quelles les colonnes numerotees ls_id prennent les valeurs ls_vals"""

    res = []
    for i in range(0, len(dat)):   #ATTENTION CHANGEMENT ON PART A 0. UN VOXEL ETAIT MANQUANT SINON !! 20/12/2011 MARC SAUDREAU
        bol = 1
        for j in range(len(ls_id)):
            if dat[i][ls_id[j]] == ls_vals[j]:
                bol = bol*1
            else :
                bol = bol*0

        if bol == 1:
            res.append(dat[i])

    return res

def t_list(tab):
    """transpose tab"""
    res = []
    if tab:
        for j in range(len(tab[0])):
            v = []
            for i in range(len(tab)):
                v.append(tab[i][j])

            res.append(v)

    return res
