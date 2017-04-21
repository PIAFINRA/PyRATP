""" Class interface for Z+ oriented / autofit equivalent of RATP grid"""
import numpy
import pandas
from alinea.pyratp.grid import Grid


def relative_index(x, dx):
    """ compute the cell index of a coordinate x in a dx cell-wide 1D grid starting at zero with [lower_bound, upper_bound[ cell boundaries.
    negative index are used if x < 0.
    """
    x = numpy.array(x)
    min_index = numpy.floor(min(x) / float(dx))
    max_index = numpy.ceil(max(x) / float(dx))
    bins = numpy.arange(min_index * dx, (max_index + 2) * dx, dx)
    return min_index + pandas.cut(x, bins, right=False, labels=False)


class SmartGrid(object):
    """ A class interface for a natural (Z+ -> sky) auto-fittable  RATP grid"""
    default = {'shape': [10, 10, 10], 'resolution': [0.1, 0.1, 0.1],
               'origin': (0, 0, 0)}

    def __init__(self, scene_box =None, shape=None, resolution=None,
                 toric=False, domain=None, z_soil=None, x_dz=None):
        """
        Initialise a grid. All inputs are expected to be meters

        Arguments:
        scene_box: a ((xmin, ymin, zmin), (xmax, ymax, zmax)) scene bounding
         box tuple. If None, a default grid is set-up
        shape: dimensions of the grid (voxel number per axis: [nx, ny, nz]).
         If None, shape will adapt to scene, using grid_resolution.
        resolution: size (m) of voxels in x,y and z direction :[dx, dy, dz].
         If None, resolution will adapt to scene using grid_shape.
        toric (bool): False (default) if the scene is an isolated canopy,
         True if the scene is toric, ie simulated as if repeated indefinitvely
        domain: a ((xmin, ymin), (xmax, ymax)) tuple of coordinates
         (in scene units) describing the spatial extent of the toric scene
         pattern domain. If None (default) the scene bounding box will be taken
          as the domain
        z_soil : z coordinate (scene units) of the soil in the scene. If None
        (default), soil will be positioned at the base of the canopy bounding box
        x_dz (optional): tuple decribing x individual voxel size (m) in
        z direction (from the soil to the top of the canopy). If None (default),
         homogeneous z grid_resolution is used.

        """

        self.z_soil = z_soil
        self.toric = toric
        self.domain = domain
        self.x_dz = x_dz

        xo, yo, zo = self.default['origin']
        xmax, ymax, zmax = None, None, None
        if scene_box is not None:
            (xo, yo, zo), (xmax, ymax, zmax) = scene_box
            if resolution is None and shape is None:
                # make as if shape was not None to trigger resolution
                # adjustment only  for this special case
                shape = self.default['shape']
        if domain is not None:
            (xo, yo), (xmax, ymax) = domain
        if z_soil is None:
            self.z_soil = zo
        else:
            zo = z_soil

        dx, dy, dz = self.default['resolution']
        nbx, nby, nbz = self.default['shape']
        if resolution is not None:
            dx, dy, dz = resolution
        if shape is not None:
            nbx, nby, nbz = shape

        if resolution is None and xmax is not None:
            if toric:
                # toric canopies allows coordinate outside the pattern
                dx = (xmax - xo) / float(nbx)
                dy = (ymax - yo) / float(nby)
            else:
                # use nbx -1 to ensure min and max are in the grid
                if nbx > 1:
                    dx = (xmax - xo) / float(nbx - 1)
                else:
                    dx = (xmax - xo) * 1.01
                if nby > 1:
                    dy = (ymax - yo) / float(nby - 1)
                else:
                    dy = (ymax - yo) * 1.01

            if nbz > 1:
                dz = (zmax - zo) / float(nbz - 1)
            else:
                dz = (zmax - zo) * 1.01
            # try to accomodate flat scene
            if dx == dy == dz == 0:
                dx = dy = dz = 0.01
            if dz == 0:
                dz = (dx + dy) / 2.
            if dx == 0:
                dx = (dy + dz) / 2.
            if dy == 0:
                dy = (dx + dz) / 2.

        if shape is None and xmax is not None:
            if domain is None:
                nbx = int(numpy.ceil((xmax - xo) / float(dx)))
                nby = int(numpy.ceil((ymax - yo) / float(dy)))
                if not toric:
                    #ensure max are in the grid in the case xmax - xo
                    # is a multiple of dx
                    if not xmax < xo + dx * nbx:
                        nbx += 1
                    if not ymax < yo + dy * nby:
                        nby += 1
            else: #dx,dy,dz are adjusted to fit the domain exactly
                nbx = int((xmax - xo) / float(dx))
                nby = int((ymax - yo) / float(dy))
                dx = (xmax - xo) / float(nbx)
                dy = (ymax - yo) / float(nby)
            nbz = int(numpy.ceil((zmax - zo) / float(dz)))
            if not zmax < zo + dz * nbz:
                nbz += 1

        if xmax is not None:
            # balance extra-space between both sides of the grid (except z if zsoil
            #  has been set)
            extrax = dx * nbx - (xmax - xo)
            xo -= (extrax / 2.)
            extray = dy * nby - (ymax - yo)
            yo -= (extray / 2.)
            if z_soil is None:
                extraz = dz * nbz - (zmax - zo)
                zo -= (extraz / 2.)

        # dz for all voxels
        if x_dz is not None:
            if zmax is not None:
                if zmax > zo + sum(x_dz):
                    raise ValueError('zmax does not fit in the grid')
            dz = x_dz
            nbz = len(dz)

        self.origin = xo, yo, zo
        self.shape = nbx, nby, nbz
        self.resolution = dx, dy, dz

    def bbox(self):
        """ return lower and upper corner of the grid"""
        xo, yo, zo = self.origin
        dx, dy, dz = self.resolution
        nbx, nby, nbz = self.shape

        lower = xo, yo, zo
        if self.x_dz is None:
            upper = xo + nbx * dx, yo + nby * dy, zo + nbz * dz
        else:
            upper = xo + nbx * dx, yo + nby * dy, sum(dz)

        return lower, upper

    def grid_index(self, x, y, z, check=False):

        xo, yo, zo = self.origin
        dx, dy, dz = self.resolution
        nbx, nby, nbz = self.shape

        x = numpy.array(x) - xo
        y = numpy.array(y) - yo
        z = numpy.array(z) - zo

        jx = relative_index(x, dx)
        jy = relative_index(y, dy)

        if self.toric:
            jx = jx % nbx
            jy = jy % nby

        if self.x_dz is None:
            jz = relative_index(z, dz)
        else:
            # dh is for the upper boundary of cells from base to top
            dh = numpy.cumsum(dz)
            jz = numpy.searchsorted(dh, z, 'right')

        if check:
            if any(numpy.logical_or(jx < 0, jx >= nbx)):
                raise ValueError('some x values are outside the grid')
            if any(numpy.logical_or(jy < 0, jy >= nby)):
                raise ValueError('some y values are outside the grid')
            if any(numpy.logical_or(jz < 0, jz >= nbz)):
                raise ValueError('some z values are outside the grid')

        return jx, jy, jz

    def cell_relative_coordinates(self, x, y, z, normalise = True):
        """ transform x, y, z coordinates in the frame relative to the grid cell
        the points belong

        Args:
            x: array-like
            y: array-like
            z: array-like
            normalise: should relative coordinates be normalised by cell
             dimensions ?

        Returns:
            xv, yv, zv the relative coordinates of pooints
        """
        dx, dy, dz = self.resolution
        nbx, nby, nbz = self.shape
        delta_x = nbx * dx
        delta_y = nby * dy

        if self.toric:
            x %= delta_x
            y %= delta_y

        jx, jy, jz = self.grid_index(x, y, z)

        xv = x - jx * dx
        yv = y - jy * dy

        if self.x_dz is None:
            zv = z - jz * dz
        else:
            # dh is for the upper boundary of cells from base to top
            dh = dz.cumsum()
            zv = z - numpy.array([dh[j] for j in jz])

        # normalising voxel dimensions
        if normalise:
            xv /= dx
            yv /= dy
            if self.x_dz is None:
                zv /= dz
            else:
                zv /= numpy.array([dz[j] for j in jz])

        return xv, yv, zv

    def ratp_grid_parameters(self):
        xo, yo, zo = self.origin
        dx, dy, dz = self.resolution
        nbx, nby, nbz = self.shape
        pars={}
        pars['toric'] = self.toric
        pars['xorig'], pars['yorig'] = xo, yo
        # zorig is a z offset in grid.py (grid_z = z + zo)
        pars['zorig'] = -zo
        pars['njx'], pars['njy'], pars['njz'] = nbx, nby, nbz
        pars['dx'], pars['dy'] = dx, dy
        # dz is from top to base for ratp
        if self.x_dz is None:
            pars['dz'] = [dz] * nbz
        else:
            pars['dz'] = dz[::-1]
        return pars

    def ratp_grid_index(self, jx, jy, jz):
        nbx, nby, nbz = self.shape
        jjx = jx
        jjy = nby - jy - 1
        jjz = nbz - jz - 1
        return map(lambda x: x.astype(int).tolist(), [jjx, jjy, jjz])

    def ratp_grid(self, surfacic_point_cloud, rsoil=0.2, latitude=43,
                  longitude=3, orientation=0, timezone=0, idecaly=0):
        """ Create a (filled) Ratp grid and compute associated grid indices

        Args:
            surfacic_point_cloud:
            rsoil:
            latitude:
            longitude:
            orientation:
            timezone:
            idecaly:

        Returns:

        """

        spc = surfacic_point_cloud

        if not hasattr(rsoil, '__len__'):
            rsoil = [rsoil]

        grid_pars = {'latitude': latitude,
                     'longitude': longitude,
                     'timezone': timezone,
                     'idecaly': idecaly,
                     'orientation': orientation,
                     'rs': rsoil,
                     'nent': spc.entities()}

        grid_pars.update(self.ratp_grid_parameters())
        grid = Grid.initialise(**grid_pars)
        grid_indices = self.grid_index(spc.x, spc.y, spc.z, check=True)
        jx, jy, jz = self.ratp_grid_index(*grid_indices)
        entity = spc.entity - 1  # Grid.fill expect python indices
        grid, _ = Grid.fill_from_index(entity, jx, jy, jz, spc.area,
                                       spc.nitrogen, grid)
        # create smart_grid index dict
        jx, jy, jz = grid_indices
        indices = {'jx': jx, 'jy': jy, 'jz': jz}

        return grid, indices
