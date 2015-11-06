""" Unit tests for RatpScene module
"""
from alinea.pyratp.RatpScene import RatpScene

from openalea.plantgl import all as pgl

def scene():
    s = pgl.Scene()
    #s.add(pgl.Sphere(slices=64,stacks=64))
    s.add(pgl.Sphere())
    return s

def test_init():
    s = RatpScene()
    
    sc = scene()
    s = RatpScene(sc)
    
    return s
    
    
def test_fitgrid():

    sc = scene()
    s = RatpScene(sc)

    return s.fit_grid()
    
def test_scene_transform():

    sc = scene()
    s = RatpScene(sc)

    return s.scene_transform()
    
def test_grid():
    sc = scene()
    s = RatpScene(sc)
    
    return s.grid()
    
def test_irradiation():
    sc = scene()    
    s = RatpScene(sc)
    return s.do_irradiation()
    
def test_plot(**args):
    sc = scene()
    s = RatpScene(sc,**args)
    res = s.do_irradiation()
    s.plot(res[res['Iteration'] == 1])
    
