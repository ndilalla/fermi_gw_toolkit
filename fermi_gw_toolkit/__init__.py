__author__ = 'giacomov'

import os
import site

PACKAGE_NAME = 'fermi_gw_toolkit'

FERMI_GW_ROOT = os.path.abspath(os.path.dirname(__file__))

VERBOSE = False

def _print(msg, verbose=True):
    if verbose:
        print(msg)

try:
    GPL_TASKROOT = os.environ['GPL_TASKROOT']
except:
    GPL_TASKROOT = FERMI_GW_ROOT.split(PACKAGE_NAME)[0]
_print('GPL_TASKROOT directory set to: %s' % GPL_TASKROOT, verbose=VERBOSE)

try:
    FERMI_GW_DATA = os.environ['FERMI_GW_DATA']
    _print('Fermi data directory set to: %s' % FERMI_GW_DATA, verbose=VERBOSE)
except:
    _print('You have to set FERMI_GW_DATA before proceding with the analysis.',\
           verbose=VERBOSE)

try:
    FERMI_GW_OUTPUT = os.environ['FERMI_GW_OUTPUT']
except:
    FERMI_GW_OUTPUT = FERMI_GW_ROOT
_print('Output directory set to: %s ' % FERMI_GW_OUTPUT, verbose=VERBOSE)

try:
    GTBURST_PATH = os.environ['GTBURST_PATH']
except:
    site_pkg = site.getsitepackages()[0]
    GTBURST_PATH = os.path.join(site_pkg, 'fermitools', 'GtBurst')
_print('GtBurst directory set to: %s ' % GTBURST_PATH, verbose=VERBOSE)

try:
    DECORATOR_PATH = os.environ['DECORATOR_PATH']
except:
    DECORATOR_PATH = 'http://glast-ground.slac.stanford.edu/Decorator/exp/Fermi/Decorate/groups/grb/GWFUP//'
_print('Decorator path set to: %s ' % DECORATOR_PATH, verbose=VERBOSE)

