# Header
#

"""

"""

from alinea.pyratp import pyratp
import os
import shutil
import tempfile

#import pyRATP
class runRATP(object):
    """
    """
    def __init__(self, *args, **kwds):
        """
        """
        pass
    @staticmethod
    def DoAll(*args):
        print 'DOALL'
        if os.path.isdir("c:/tmpRATP"):
            shutil.rmtree("c:/tmpRATP")
        path = '/tmp/tmpRATP'
        #os.mkdir("c:/tmpRATP/")
        os.mkdir(path+"/Resul")

        pyratp.ratp.do_all()
