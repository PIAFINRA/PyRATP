# -*-python-*-

import os
from openalea.sconsx import config, environ


ALEASolution = config.ALEASolution

pj = os.path.join

SConsignFile()

options = Variables(['../options.py', 'options.py'], ARGUMENTS)
#tools = ['f2py']
tools = ['install']

env = ALEASolution(options, tools)

# Set build directory
prefix = env['build_prefix']

# Build stage
SConscript(pj(prefix,"src/f90/SConscript"), exports="env")

Default("build")
