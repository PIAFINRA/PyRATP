""" Unit tests for RatpScene module
"""
from alinea.pyratp.RatpScene import RatpScene

from openalea.plantgl import all as pgl

def scene():
    s = pgl.Scene()
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
    vfn = './vegetationa_2004.vfn'
    sky = './skyvaultsoc.skv'
    met = './mmeteo082050_1h.mto'
    
    s = RatpScene(sc)
    return s.do_irradiation(vfn, sky, met)
    
def test_plot():
    sc = scene()
    vfn = './vegetationa_2004.vfn'
    sky = './skyvaultsoc.skv'
    met = './mmeteo082050_1h.mto'
    
    s = RatpScene(sc)
    res = s.do_irradiation(vfn, sky, met)
    s.plot(res[res['Iteration'] == 1])
    
