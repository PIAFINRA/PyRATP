""" unit tests for clumping_index
"""
import numpy
from alinea.pyratp.clumping_index import clark_evans

def test_index():

    #a regular 3D grid
    vals= numpy.linspace(0,1,10)
    pts = [(x,y,z) for x in vals for y in vals for z in vals]
    domain = ((0,0,0), (1,1,1))
    print 'grid', clark_evans(pts, domain, filter_boundary=False)
    print 'grid corrected', clark_evans(pts, domain, filter_boundary=True)
    
    # a 2D random sample
    x, y = numpy.random.random_sample((2,100))
    pts = zip(x,y)
    domain = ((0,0), (1,1))
    print 'random2D', clark_evans(pts, domain, filter_boundary=False)
    print 'random2D corrected', clark_evans(pts, domain, filter_boundary=True)
    
    # a 3D random sample
    x, y, z = numpy.random.random_sample((3,100))
    pts = zip(x,y,z)
    domain = ((0,0,0), (1,1,1))
    print 'random3D', clark_evans(pts, domain, filter_boundary=False)
    print 'random3D corrected', clark_evans(pts, domain, filter_boundary=True)