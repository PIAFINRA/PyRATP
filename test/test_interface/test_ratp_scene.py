import numpy
from alinea.pyratp.interface.ratp_scene import RatpScene, pgls


def test_instanciation():
    ratp = RatpScene()
    numpy.testing.assert_almost_equal(ratp.smart_grid.bbox(),
                                      ((-0.05, -0.05, -0.55),
                                       (1.05, 1.05, 0.55)), decimal=2)
    numpy.testing.assert_almost_equal(ratp.scene.normals,
                                      [[0., 0., 1.], [0., 0., 1.]])
    for w in ('city', 'latitude', 'longitude'):
        assert w in ratp.localisation
    assert isinstance(ratp.entities, dict)
    assert len(ratp.entity_code) == ratp.scene.size


    ratp = RatpScene(shape=[5, 5, 10])
    numpy.testing.assert_array_equal(ratp.smart_grid.shape, [5, 5, 10])

    if pgls.pgl_imported:
        scene = pgls.pgl.Scene([pgls.pgl.Sphere()])
        ratp = RatpScene(scene)
        numpy.testing.assert_almost_equal(ratp.smart_grid.bbox(), (
        (-0.55, -0.55, -0.55), (0.55, 0.55, 0.55)), decimal=2)
        assert 'shape_id' in ratp.scene.properties
        assert ratp.scene.size == 112
        assert len(ratp.entity_code) == 112


def test_n_entities():
    ratp = RatpScene()
    assert ratp.n_entities() == 1


def test_clumping():
    ratp = RatpScene()
    mu = ratp.clumping()
    assert len(mu) == 1


def test_grid():
    ratp = RatpScene()
    grid = ratp.grid()
    assert grid.s_canopy == 1
    numpy.testing.assert_almost_equal(grid.total_ground_area, 1.2345678)
    vindex = ratp.voxel_index()


def test_inclination_distribution():
    ratp = RatpScene()
    distinc = ratp.inclination_distribution()
    numpy.testing.assert_array_equal(distinc[0],
                                     [1., 0., 0., 0., 0., 0., 0., 0., 0.])


def test_light():
    ratp = RatpScene(resolution=(1, 1, 1))
    dfvox = ratp.do_irradiation()
    dfpoints = ratp.scene_lightmap(dfvox, 'point_id')
    dfshape = ratp.scene_lightmap(dfvox, 'shape_id')
    if pgls.pgl_imported:
        ratp.plot(dfvox)
        ratp.plot(dfvox, 'shape_id')
        ratp = RatpScene(pgls.unit_sphere_scene())
        dfvox = ratp.do_irradiation()
        ratp.plot(dfvox)



