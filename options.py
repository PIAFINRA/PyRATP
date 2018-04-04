#scons parameters file
#use this file to pass custom parameter to SConstruct script

import sys
if(sys.platform.startswith('win')):
    #compiler='msvc'
    compiler= 'mingw' # by default on windows

