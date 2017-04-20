from openalea.plantgl import all as pgl

def shape_as_mesh(pgl_shape, discretiser = None):
    if discretiser is None:
        discretiser = pgl.Discretizer()
    discretiser.process(pgl_shape)
    tset = discretiser.result
    return tset.pointList, tset.indexList