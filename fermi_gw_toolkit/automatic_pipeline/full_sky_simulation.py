import logging
import glob
import os
from configuration import config
import numpy as np

from GtApp import GtApp
from GtBurst import IRFS

from utils import fail_with_error, execute_command, DataNotAvailable

try:

    import astropy.io.fits as pyfits

except ImportError:

    import pyfits

logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("full_sky_simulation.py")
log.setLevel(logging.DEBUG)


class CustomSimulator(object):
    """

        :param ft2:
        :param tstart:
        :param simulation_time:
        :param irfs:
        :param emin:
        :param emax:
        :param ltfrac:
        """
    def __init__(self, ft2, tstart, simulation_time,
                 irfs="P8R2_SOURCE_V6", emin=100, emax=100000, ltfrac=0.9):
        """

        :param ft2:
        :param tstart:
        :param simulation_time:
        :param irfs:
        :param emin:
        :param emax:
        :param ltfrac:
        """
        self._ft2 = ft2
        self._tstart = tstart
        self._simulation_time = simulation_time
        self._irfs = irfs
        self._emin = emin
        self._emax = emax
        self._ltfrac = ltfrac

        # This will contain the list of temporary files produced
        self._temp_files = []

    def run_simulation(self, outfile='gwt_sim', seed=None):
        """

        :param outfile:
        :param seed:
        :return:
        """

        # We need to setup the environment variable SKYMODEL_DIR before running gtobssim
        os.environ['SKYMODEL_DIR'] = config.get("SLAC", "SKYMODEL_DIR")

        # Gather arguments for gtobssim in a dictionary

        evroot = '__gw_sims'

        _gtobssim_args = {'emin': self._emin,
                          'emax': self._emax,
                          'edisp': 'yes',
                          'infile': config.get("SLAC", "SIM_XML"),
                          'srclist': config.get("SLAC", "SIM_SRC_LIST"),
                          'scfile': self._ft2,
                          'evroot': evroot,
                          'simtime': self._simulation_time,
                          'ltfrac': self._ltfrac,
                          'tstart': self._tstart,
                          'use_ac': 'no',
                          'irfs': self._irfs,
                          'evtype': 'none',
                          'seed': seed if seed is not None else np.random.randint(int(1e4), int(1e9))
                          }

        gtobssim_app = GtApp('gtobssim')

        gtobssim_app.run(**_gtobssim_args)

        # Now find out the FT1 file produced by the simulation
        event_files = glob.glob("%s_events_*.fits" % evroot)

        assert len(event_files) > 0, "Simulation failed, there are no ft1 files produced."

        # Track them as temp files so we'll clean them up at the end
        event_files = map(self._track_temp_file, event_files)

        # Merge the event files using gtselect

        # Make a text file with the list of ft1 files
        ft1_file_list = self._track_temp_file("__gw_sim_ft1_list.txt")

        with open(ft1_file_list, "w+") as f:

            for ft1 in event_files:

                f.write("%s\n" % ft1)

        gtselect_app = GtApp('gtselect')

        gtselect_app.run(infile=ft1_file_list, outfile=outfile,
                         ra=0.0, dec=0.0, rad=180.0,
                         tmin=self._tstart, tmax=self._tstart + self._simulation_time,
                         emin=self._emin, emax=self._emax,
                         zmax=180.0,
                         evclass=IRFS.IRFS[self._irfs].evclass,
                         evtype="INDEF",
                         convtype='-1')

        # Now check how many events we had before gtselect
        n_simulated_events = 0

        for ft1 in event_files:

            with pyfits.open(ft1) as f:

                n_simulated_events += len(f['EVENTS'])

        # Now get the number of events which survived the cut
        n_simulated_events_after_cuts = 0

        with pyfits.open(outfile) as f:

            n_simulated_events_after_cuts += len(f['EVENTS'])

        assert n_simulated_events == n_simulated_events_after_cuts, "Some events were lost when cutting with gtselect!"

    def _track_temp_file(self, filename):

        self._temp_files.append(filename)

        return os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))

    def run_gtdiffrsp(self):

        pass

        #gtdiffrsp_args = {'evfile':}

        # evfile, f, a, "/afs/slac.stanford.edu/u/gl/giacomov/workspace/DATA/GRBOUT/081102365/081102365_events__ROI_0.000_2.000.fits",, , "Event data file"
        # evtable, s, h, "EVENTS",, , "Event data extension"
        # scfile, f, a, "/afs/slac.stanford.edu/u/gl/giacomov/workspace/DATA/FITS/LAT/081102365_P8_P302_BASE_ft2_247307702_247358302.fits",, , "Spacecraft data file"
        # sctable, s, h, "SC_DATA",, , "Spacecraft data extension"
        # srcmdl, fr, a, "/afs/slac.stanford.edu/u/gl/giacomov/workspace/DATA/GRBOUT/081102365/081102365_model__ROI_0.000_2.000.xml",, , "Source model file"
        # irfs, s, a, "P8R2_TRANSIENT020E_V6",, , "Response functions to use"
        # evclsmin, i, h, 0,, , "Minimum event class level"
        # evclass, i, h, INDEF,, , "Target class level"
        # evtype, i, h, INDEF,, , "Event type selections"
        # convert, b, h, no,, , "convert header to new diffrsp format?"
        #
        # chatter, i, h, 2, 0, 4, Output
        # verbosity
        # clobber, b, h, no,, , "Overwrite existing output files"
        # debug, b, h, no,, , "Activate debugging mode"
        # gui, b, h, no,, , "GUI mode activated"
        # mode, s, h, "ql",, , "Mode of automatic parameters"


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
