
"""
   Presentation ALEA :  REA Decembre 2003
   **************************************
"""

######################################################
# Loading and exploring a digitized Plant with AMAPmod
######################################################
from amlPy import *

def xx(x) :
    f= Feature(x, "XX")
    return f if f else Undef

def yy(x) :
    f= Feature(x, "YY")
    return f if f else Undef

def zz(x) :
    f= Feature(x, "ZZ")
    return f if f else Undef
    
def aa(x) : return  Feature(x, "AA") # ne peut pas rajouter 180 AML+int
def bb(x) : return  Feature(x, "BB")
def cc(x) : return  Feature(x, "CC")

def leaf_len(x) :
    return 18. if Class(x) == 'F' else Undef

def leaf_dia(x) :
    return 2. if Class(x) == 'F' else Undef

def eulerf(x) : return False

def color1(x):
    c = Class(x)
    if c == 'F':
        return Red
    elif c == 'U':
        return Green
    else:
        return Blue

def lineTree(mtg, drf):
    g1 = MTG(mtg)

    plants = VtxList(Scale=1)
    s= """

    dr = DressingData(drf)
    f1 = PlantFrame( plants[0], Scale=3, XX=xx, YY=yy, ZZ=zz,
                     Length= leaf_len,
                     TopDiameter=leaf_dia, BottomDiameter=leaf_dia,
                     EulerAngles=eulerf, AA=aa, BB=bb, CC=cc,
                     DressingData=dr)

"""
    f1 = PlantFrame( plants[0], Scale=3)

    lt = Plot(f1, Color=color1)
    return lt            

