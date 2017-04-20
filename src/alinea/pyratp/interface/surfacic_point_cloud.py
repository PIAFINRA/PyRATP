import pandas
import numpy


def norm(vector):
    x, y, z = vector
    return numpy.sqrt(x ** 2 + y ** 2 + z ** 2)


def normed(vector):
    """ normalised coordinates of (0,point) vector
    """
    return numpy.array(vector) / norm(vector)


def surface(face, vertices):
    A, B, C = [numpy.array(vertices[i]) for i in face]
    return norm(numpy.cross(B - A, C - A)) / 2.0


def normal(face, vertices):
    A, B, C = [numpy.array(vertices[i]) for i in face]
    return normed(numpy.cross(B - A, C - A))


def centroid(face, vertices):
    points = [numpy.array(vertices[i]) for i in face]
    x, y, z = zip(*points)
    return numpy.mean(x), numpy.mean(y), numpy.mean(z)


class SurfacicPointCloud(object):
    """Data structure for handling a ratp-compatible canopy"""

    units = {'mm': 0.001, 'cm': 0.01, 'dm': 0.1, 'm': 1, 'dam': 10, 'hm': 100,
             'km': 1000}
    units_w = {'mg': 0.001, 'g': 1, 'kg': 1000}

    def __init__(self, x, y, z, area, entity=None, nitrogen=None, label=None,
                 unit_length='m', unit_weight='g'):
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
            label: (array-like) identifiers for objects in the canopy (optional,
             useful for aggregating RATP outputs). If None, entity is used.
            unit_length: (string) the unit used for inputs. Will be used to
            convert to meter all inputs
            unit_weight: (string) the unit used for nitrogen. Will be used to
             convert to meter all inputs

        Returns:
            a surfacic point cloud instance with all data converted to SI units
            (m,g)
        """

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

        if label is None:
            label = entity

        assert len(x) == len(y) == len(z) == len(entity) == len(area) == len(
            nitrogen) == len(label)

        self.x = numpy.array(x) * self.convert
        self.y = numpy.array(y) * self.convert
        self.z = numpy.array(z) * self.convert
        self.area = numpy.array(area) * self.convert**2
        self.entity = numpy.array(entity)
        self.nitrogen = numpy.array(nitrogen) * self.convert_w / self.convert**2
        self.label = label
        self.unit = 'm'
        self.unit_w = 'g'

        assert all(self.entity > 0)
        assert self.entity.max() == len(set(self.entity))

    @staticmethod
    def from_mesh(vertices, faces, entity=None, nitrogen=None,
                  label=None, unit_length='m', unit_weight='g'):
        """ Instantiate a SurfacicPointCloud from a mesh

        Args:
            vertices: list of mesh vertices coordinates
            faces: list of vertex idex defining mesh faces
            entity: (array-like) RATP entity codes (>=1). If None (default),
            entity 1 is used for all points.
            nitrogen: (array-like): nitrogen content. If None (default),
            a value of 2 is used for all points.
            label: (array-like) identifiers for objects in the canopy (optional,
            useful for aggregating RATP outputs). If None, entity is used.
            unit_length: (string) the unit used for inputs.
            unit_weight: (string) the unit used for nitrogen.
        Returns:
            a SurfacicPointCloud instance
        """
        areas = [surface(f, vertices) for f in faces]
        x, y, z = zip(*[centroid(f, vertices) for f in faces])
        return SurfacicPointCloud(x, y, z, areas, entity=entity,
                                  nitrogen=nitrogen, label=label,
                                  unit_length=unit_length,
                                  unit_weight=unit_weight)

    def entities(self):
        """ return the number of distinct entities in the canopy"""
        return self.entity.max()

    def as_data_frame(self):
        df = pandas.DataFrame({'label': self.label, 'x': self.x, 'y': self.y,
                               'z': self.z, 'VegetationType': self.entity,
                               'area': self.area, 'nitrogen': self.nitrogen})
        return df

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
        return SurfacicPointCloud(x=d['x'], y=d['y'], z=d['z'], area=d['area'],
                                  entity=d['VegetationType'],
                                  nitrogen=d['nitrogen'], label=d['label'])

    def bounding_box(self):
        return self.x.min(), self.y.min(), self.z.min(), self.x.max(), \
               self.y.max(), self.z.max()
