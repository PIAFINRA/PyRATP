import numpy
import os
import tempfile

from alinea.pyratp.interface.surfacic_point_cloud import normed, spherical, \
    cartesian, surface, normal, centroid, random_normals, SurfacicPointCloud


def test_spherical():
    v = normed((1, 0, 1))
    theta, phi = spherical(v)
    assert phi == 0
    numpy.testing.assert_almost_equal(theta, numpy.pi / 4)
    cart = cartesian(theta, phi)
    numpy.testing.assert_almost_equal(cart, v)


def test_triangle_math():
    face = range(3)
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0))

    numpy.testing.assert_almost_equal(surface(face, vertices), 0.5)
    numpy.testing.assert_almost_equal(normal(face, vertices), (0, 0, 1))
    numpy.testing.assert_almost_equal(centroid(face, vertices), (1./3, 1./3, 0))


def test_random_noromals():
    n = random_normals(1)
    assert len(n) == 1
    assert len(n[0]) == 3
    n = random_normals(10)
    assert len(n) == 10
    assert len(n[0]) == 3


def test_spc_instantiation():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    for w in ('x', 'y', 'z', 'area', 'nitrogen', 'normals', 'properties'):
        assert hasattr(spc, w)
    spc = SurfacicPointCloud(100, 100, 100, 10000, nitrogen=0.2,
                             unit_length='cm', unit_weight='mg')
    assert spc.x == spc.y == spc.z == spc.area == 1  # m2
    assert spc.nitrogen == 2  # g.m-2

    faces = (range(3),)
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0))
    spc = SurfacicPointCloud.from_mesh(vertices, faces)
    assert spc.area == 0.5
    numpy.testing.assert_array_equal(spc.normals, ((0, 0, 1),))


def test_data_frame():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    df = spc.as_data_frame()
    assert df.shape == (1, 9)
    spc.properties.update({'a_property': (3,)})
    df = spc.as_data_frame()
    assert df.shape == (1, 10)


def test_serialisation():
    spc = SurfacicPointCloud(0, 0, 0, 1)
    try:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.csv')
        spc.save(path)
        spc2 = SurfacicPointCloud.load(path)
        assert spc.x == spc2.x
        numpy.testing.assert_almost_equal(spc.normals, spc2.normals)

        spc.properties.update({'a_property': (3,)})
        spc.save(path)
        spc2 = SurfacicPointCloud.load(path)
        assert 'a_property' in spc2.properties
    finally:
        os.remove(path)
        os.rmdir(tmpdir)


def test_bbox():
    faces = ((0, 1, 2), (0, 2, 0), (0, 1, 3))
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    spc = SurfacicPointCloud.from_mesh(vertices, faces)
    expected = ((0.0, 0.0, 0.0), [1. / 3] * 3)
    numpy.testing.assert_almost_equal(spc.bbox(), expected)


def test_inclinations():
    faces = ((0, 1, 2), (0, 2, 3), (0, 1, 3))
    vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    entity = (2, 1, 2)
    spc = SurfacicPointCloud.from_mesh(vertices, faces, entity=entity)
    inc = spc.entities_inclinations()
    numpy.testing.assert_array_equal(inc,[[90.0], [0.0, 90.0]])
