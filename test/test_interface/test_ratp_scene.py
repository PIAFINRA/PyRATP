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
    assert ratp.ratp_grid.s_canopy == 1
    numpy.testing.assert_almost_equal(ratp.ratp_grid.total_ground_area, 1.2345678)
    numpy.testing.assert_array_equal(ratp.distinc[0],
                                     [1., 0., 0., 0., 0., 0., 0., 0., 0.])
    vindex = ratp.voxel_index()

    ratp = RatpScene(shape=[5, 5, 10])
    numpy.testing.assert_array_equal(ratp.smart_grid.shape, [5, 5, 10])

    if pgls.pgl_imported:
        scene = pgls.pgl.Scene([pgls.pgl.Sphere()])
        ratp = RatpScene(scene)
        numpy.testing.assert_almost_equal(ratp.smart_grid.bbox(), (
        (-0.55, -0.55, -0.55), (0.55, 0.55, 0.55)), decimal=2)
        assert 'shape_id' in ratp.scene.as_data_frame().columns
        assert ratp.scene.size == 112
        assert len(ratp.entity_code) == 112


def test_parameters():
    ratp = RatpScene()
    pars = ratp.parameters()
    assert 'grid' in pars
    assert isinstance(pars['grid'], dict)


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



