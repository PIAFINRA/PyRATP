from alinea.pyratp import pyratp
from alinea.pyratp import grid
import alinea.pyratp.pyratp as r

def test_read():
    fn = 'essaiRATP2/RATP/grille/grid3Da_2004.grd'
    g = grid.Grid()
    g.read(fn)

    grid3d = r.grid3d
    assert (grid3d.njx, grid3d.njy ,grid3d.njz) == (19,20,18)
    assert 0.19 <= grid3d.dx <= 0.21
