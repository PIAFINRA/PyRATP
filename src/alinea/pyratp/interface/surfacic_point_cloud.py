import pandas
import numpy


def norm(vector):
    x, y, z = vector
    return numpy.sqrt(x ** 2 + y ** 2 + z ** 2)


def normed(vector):
    """ normalised coordinates of (0,point) vector
    """
    return numpy.array(vector) / norm(vector)


def spherical(vector):
    """ inclination (theta) and azimuth (phi) spherical angles"""
    x, y, z = normed(vector)
    theta = numpy.arccos(z)
    phi = numpy.arctan2(y, x)
    return theta, phi


def cartesian(theta, phi):
    """ cartesian coordinates of a unit vector with inclination theta and
    azimuth phi"""
    x = numpy.sin(theta) * numpy.cos(phi)
    y = numpy.sin(theta) * numpy.sin(phi)
    z = numpy.cos(theta)
    return x, y, z


def surface(face, vertices):
    a, b, c = [numpy.array(vertices[i]) for i in face]
    return norm(numpy.cross(b - a, c - a)) / 2.0


def normal(face, vertices):
    a, b, c = [numpy.array(vertices[i]) for i in face]
    return normed(numpy.cross(b - a, c - a))


def centroid(face, vertices):
    points = [numpy.array(vertices[i]) for i in face]
    x, y, z = zip(*points)
    return numpy.mean(x), numpy.mean(y), numpy.mean(z)


def random_normals(size=1):
    theta = numpy.pi / 2 * numpy.random.random_sample(size)
    phi = 2 * numpy.pi * numpy.random.random_sample(size)
    return zip(*cartesian(theta, phi))


class SurfacicPointCloud(object):
    """Python data structure for handling a ratp-suited canopy"""

    units = {'mm': 0.001, 'cm': 0.01, 'dm': 0.1, 'm': 1, 'dam': 10, 'hm': 100,
             'km': 1000}
    units_w = {'mg': 0.001, 'g': 1, 'kg': 1000}

    def __init__(self, x, y, z, area, entity=None, nitrogen=None, normals=None,
                 properties=None, unit_length='m', unit_weight='g'):
        """Instantiate a SurfacicPointCloud canopy

        Args:
            x: (array-like) x-coordinate of surfacic elements
            y: (array-like) y-coordinate of surfacic elements
            z: (array-like) z-coordinate of surfacic elements
            area: (array-like) areas of surfacic elements
            entity: (array-like) RATP entity codes (>=1). If None (default),
             entity 1 is used for all points. Entities allows varying angles,
             mu and optical properties
            nitrogen: (array-like): nitrogen content. If None (default),
             a value of 2 is used for all points.
            normals: (array of 3-tuples): coordinates of vector normal to
             surfacic point. If None normals are randomly sampled.
            properties: (name:array-like dict) optional additional
                named data associated to surfacic points.
            unit_length: (string) the unit used for inputs. Will be used to
            convert to meter all inputs
            unit_weight: (string) the unit used for nitrogen. Will be used to
             convert to meter all inputs

        Returns:
            a surfacic point cloud instance with all data converted to SI units
            (m,g)
        """

        x, y, z, area = map(lambda v: numpy.array(v, ndmin=1), (x, y, z, area))

        try:
            self.convert = self.units[unit_length]
        except KeyError:
            print 'Warning, unit', unit_length, 'not found, meter assumed'
            self.convert = 1

        try:
            self.convert_w = self.units_w[unit_weight]
        except KeyError:
            print 'Warning, unit', unit_weight, 'not found, meter assumed'
            self.convert_w = 1

        if entity is None:
            entity = [1] * len(x)

        if nitrogen is None:
            nitrogen = [2] * len(x)

        entity, nitrogen = map(lambda v: numpy.array(v, ndmin=1),
                               (entity, nitrogen))

        if normals is None:
            normals = random_normals(len(x))

        if properties is None:
            properties = {}

        assert len(x) == len(y) == len(z) == len(entity) == len(area) == len(
            nitrogen) == len(normals)
        for k, v in properties.iteritems():
            assert len(v) == len(x)

        self.x = x * self.convert
        self.y = y * self.convert
        self.z = z * self.convert
        self.area = area * self.convert**2
        self.entity = entity
        self.nitrogen = nitrogen * self.convert_w / self.convert**2
        self.normals = normals
        self.properties = properties
        self.unit = 'm'
        self.unit_w = 'g'

        assert all(self.entity > 0)
        assert self.entity.max() == len(set(self.entity))

    @staticmethod
    def from_mesh(vertices, faces, entity=None, nitrogen=None,
                  properties=None, unit_length='m', unit_weight='g'):
        """ Instantiate a SurfacicPointCloud from a mesh

        Args:
            vertices: list of mesh vertices coordinates
            faces: list of vertex idex defining mesh faces
            entity: (array-like) RATP entity codes (>=1). If None (default),
            entity 1 is used for all points.
            nitrogen: (array-like): nitrogen content. If None (default),
            a value of 2 is used for all points.
            properties: (name:array-like dict) optional additional
                named data associated to surfacic points.
            useful for aggregating RATP outputs). If None, entity is used.
            unit_length: (string) the unit used for inputs.
            unit_weight: (string) the unit used for nitrogen.
        Returns:
            a SurfacicPointCloud instance and a list of normals
        """
        areas = [surface(f, vertices) for f in faces]
        x, y, z = zip(*[centroid(f, vertices) for f in faces])
        normals = [normal(f, vertices) for f in faces]
        return SurfacicPointCloud(x, y, z, areas, entity=entity,
                                  nitrogen=nitrogen, normals=normals,
                                  properties=properties,
                                  unit_length=unit_length,
                                  unit_weight=unit_weight)

    def n_entities(self):
        """ return the number of distinct entities in the canopy"""
        return self.entity.max()

    def as_data_frame(self):
        nx, ny, nz = zip(*self.normals)
        df = pandas.DataFrame({'x': self.x, 'y': self.y,
                               'z': self.z, 'VegetationType': self.entity,
                               'area': self.area, 'nitrogen': self.nitrogen,
                               'norm_x': nx, 'norm_y': ny, 'norm_z': nz})
        dfp = pandas.DataFrame(self.properties)
        return pandas.concat((df, dfp), axis=1)

    def save(self, path='surfacic_point_cloud.csv'):
        """ Save a csv representation of the object
        """
        df = self.as_data_frame()
        df.to_csv(path, index=False)
        return path

    @staticmethod
    def load(path='surfacic_point_cloud.csv'):
        df = pandas.read_csv(path)
        d = df.to_dict('list')
        cols = (
            'x', 'y', 'z', 'area', 'VegetationType', 'nitrogen', 'norm_x',
            'norm_y', 'norm_z')
        properties = {k: v for k, v in d.iteritems() if k not in cols}
        normals = zip(d['norm_x'], d['norm_y'], d['norm_z'])
        return SurfacicPointCloud(x=d['x'], y=d['y'], z=d['z'], area=d['area'],
                                  entity=d['VegetationType'],
                                  nitrogen=d['nitrogen'], normals=normals,
                                  properties=properties)

    def bbox(self):
        return (self.x.min(), self.y.min(), self.z.min()), (self.x.max(), \
               self.y.max(), self.z.max())

    def spherical(self):
        """ return inclination and azimuth angles of scene normals"""
        return zip(*map(spherical, self.normals))

    def entities_inclinations(self):
        """ list of inclinations angles of normals (degrees, positive) for the
        different entities"""
        theta, phi = self.spherical()
        inclin = numpy.degrees(theta)
        inclin = numpy.where(inclin == 90, 90, inclin % 90)
        df = pandas.DataFrame({'entity': self.entity, 'inc': inclin})
        return [group['inc'].tolist() for name, group in df.groupby('entity')]