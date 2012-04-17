from openalea.core.alea import run
from openalea.core.pkgmanager import PackageManager

""" A unique PackageManager is created for all test of dataflow """

pm = PackageManager()
pm.init(verbose=False)

def test_complet():
    factory = pm['pyratp.demo']['complet2']
    cn = factory.instantiate()
    for i in range(5):
        cn.eval_as_expression(31)

def test_can():
    factory = pm['pyratp.demo']['RATP with Can Files']
    cn = factory.instantiate()
    cn.eval_as_expression(15)
    result = cn.node(15).get_output(0)
    
    assert len(result) == 230
    assert result.shape == (230,9)
    assert 199 < result.mean() < 200


#test_complet()
