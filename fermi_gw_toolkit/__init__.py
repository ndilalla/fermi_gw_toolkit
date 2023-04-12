__author__ = 'giacomov'

import os
import site

PACKAGE_NAME = 'fermi_gw_toolkit'

FERMI_GW_ROOT = os.path.abspath(os.path.dirname(__file__))

try:
    FERMI_GW_DATA = os.environ['FERMI_GW_DATA']
    print('Fermi data directory set to: %s' % FERMI_GW_DATA)
except:
    print('You have to set FERMI_GW_DATA before proceding with the analysis.')


try:
    FERMI_GW_OUTPUT = os.environ['FERMI_GW_OUTPUT']
except:
    FERMI_GW_OUTPUT = FERMI_GW_ROOT
print('Output directory set to: %s ' % FERMI_GW_OUTPUT)

try:
    GTBURST_PATH = os.environ['GTBURST_PATH']
except:
    site_pkg = site.getsitepackages()[0]
    GTBURST_PATH = os.path.join(site_pkg, 'fermitools', 'GtBurst')
print('GtBurst directory set to: %s ' % GTBURST_PATH)