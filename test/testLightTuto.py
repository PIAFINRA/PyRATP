""" Test python tutorial for use of Ratp
"""

import numpy as np

import openalea.plantgl.all as pgl
from alinea.pyratp.RatpScene import RatpScene


def test_pommier():

    scene = pgl.Scene(r"./pommier.geom")
    # rotate scene arround X+ then Z+ to get top of tree in Z+ and east/west 
    for sh in scene:
        sh.geometry = pgl.EulerRotated(np.radians(90), 0, np.radians(180), sh.geometry)
        
    pgl.Viewer.display(scene)
        
    ratp = RatpScene(scene, scene_unit = 'cm')
    
    out = ratp.do_irradiation(rleaf = [0.08], rsoil=0.075)
    
    ratp.plot(out)
    
    return out
    

