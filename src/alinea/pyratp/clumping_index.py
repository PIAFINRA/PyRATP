#
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>
#

""" Methods for computing clumping indices of spatial distribution
"""

import numpy
from scipy import spatial


def _density(pts):   
    coords = numpy.array(numpy.ravel(pts)).reshape(len(pts[0]),len(pts))
    mins = coords.min(1)
    maxs = coords.max(1)
    volume = numpy.prod(maxs - mins)
    return float(len(pts)) / volume

def clark_evans(pts, density=None):
    """ Compute the clark and evans index of aggregation
    
        Parameters: 
        
        - pts: a list of point coordinates (n dimensions)
        - density : the mean density of point in the domain considered. if None, density is given by number_of_points / data_bounding_box_domain
    
        Details : 
            index = mean_of_distance_to_neighrest_neighbour / mean_distance_between_individual
            
            if distribution is random, index = 1, index tends to zero if data are clumped, and tens toward 2.15 if data are arranged in a perfectly repulsive pattern
            
        Reference:
            Clark, P.J. and Evans, F.C., 1954. Distance to nearest neighbor as a measure of spatial relationships in populations. Ecology 35: 445-453
    """
    
    if density is None:
        density = _density(pts)
    
    tree = spatial.KDTree(pts)
    dist = [d[1] for d in tree.query(pts,2)[0]]
    ra = numpy.mean(dist)
    re = 1. / (2 * numpy.power(density, 1. / len(pts[0])))
    
    return float(ra) / re 
    