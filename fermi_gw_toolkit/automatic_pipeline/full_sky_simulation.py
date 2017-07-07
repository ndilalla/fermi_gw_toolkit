import logging
import sys, os
import argparse
import traceback
from configuration import config
import numpy as np

from GtApp import GtApp

from utils import fail_with_error, execute_command, DataNotAvailable

try:

    import astropy.io.fits as pyfits

except ImportError:

    import pyfits


logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("full_sky_simulation.py")
log.setLevel(logging.DEBUG)


def do_one_simulation(ft2, tstart, simulation_time, seed=None, irfs="P8R2_SOURCE_V6", emin=100, emax=100000,
                      evroot='gwt_sim', ltfrac=0.9):

    # Gather arguments for gtobssim
    gtobssim_args = {'emin': emin,
                     'emax': emax,
                     'edisp': 'yes',
                     'infile': config.get("SLAC", "SIM_XML"),
                     'srclist': config.get("SLAC", "SIM_SRC_LIST"),
                     'scfile': ft2,
                     'evroot': evroot,
                     'simtime': simulation_time,
                     'ltfrac': ltfrac,
                     'tstart': tstart,
                     'use_ac': 'no',
                     'irfs': irfs,
                     'evtype': 'none',
                     'seed': seed if seed is not None else np.random.randint(int(1e4), int(1e9))
                     }

    gtobssim_app = GtApp('gtobssim')

    # We need to setup the environment variable SKYMODEL_DIR before running gtobssim
    os.environ['SKYMODEL_DIR'] = config.get("SLAC","SKYMODEL_DIR")

    gtobssim_app.run(**gtobssim_args)



    # gtobssim
    # emin = 100
    # emax = 100000
    # edisp = yes
    # infile = "/nfs/farm/g/glast/u29/MC-tasks/skySimData/SkyModels/3FGLSkyPass8R2/xml_files.txt"
    # srclist = "/nfs/farm/g/glast/u29/MC-tasks/skySimData/SkyModels/3FGLSkyPass8R2/source_names.txt"
    # scfile = "/afs/slac.stanford.edu/u/gl/giacomov/FermiData/bn080916009/gll_ft2_tr_bn080916009_v00.fit"
    # evroot = sim
    # simtime = 10000
    # ltfrac = 0.9
    # tstart = 243211748.6
    # use_ac = no
    # irfs = P8R2_SOURCE_V6
    # evtype = none
    # seed = 4328671012