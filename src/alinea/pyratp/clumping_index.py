#
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>
#

""" Methods for computing clumping indices of spatial distribution
"""

import numpy
from scipy import spatial


def _volume(pts):   
    coords = numpy.array(numpy.ravel(pts)).reshape(len(pts[0]),len(pts))
    mins = coords.min(1)
    maxs = coords.max(1)
    return numpy.prod(maxs - mins)

def clark_evans(pts, domain_volume=None, boundary_correction = True):
    """ Compute the clark and evans index of aggregation
    
        Parameters: 
        
        - pts: a list of point coordinates (n dimensions)
        - domain : the extend of the domain considered (area, volume). if None, volume is given by data_bounding_box_domain
    
        Details : 
            index = mean_of_distance_to_neighrest_neighbour / mean_distance_between_individual
            
            if distribution is random, index = 1, index tends to zero if data are clumped, and tens toward 2.15 if data are arranged in a perfectly repulsive pattern
            
        Reference:
            Clark, P.J. and Evans, F.C., 1954. Distance to nearest neighbor as a measure of spatial relationships in populations. Ecology 35: 445-453
            Donnelly, K. (1978) Simulations to determine the variance and edge-effect of total nearest neighbour distance. In Simulation methods in archaeology, Cambridge University Press, pp 91-95
    """
    
    if domain_volume is None:
        domain_volume = _volume(pts)
        
    density = float(len(pts)) / domain_volume
    
    tree = spatial.KDTree(pts)
    dist = [d[1] for d in tree.query(pts,2)[0]]
    ra = numpy.mean(dist)
    degre = len(pts[0])
    re = 1. / (2 * numpy.power(density, 1. / degre))
    if boundary_correction:
    # Donnelly (1978) correction for border effect (to be checked for 3D)
        n = len(pts)
        boundary = numpy.power(domain_volume, 1. / degre) * 2**degre
        corec = (0.051 + 0.041 / numpy.power(n, 1. / degre)) *  boundary / n
        re = re + corec
        
    return float(ra) / re
    