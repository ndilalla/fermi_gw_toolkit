import logging
import glob
import os
from configuration import config
import numpy as np
from xml.etree import ElementTree

from GtApp import GtApp
from GtBurst import IRFS
from GtBurst.LikelihoodComponent import findTemplate
from GtBurst.getDataPath import getDataPath

from utils import fail_with_error, execute_command, DataNotAvailable

try:

    import astropy.io.fits as pyfits

except ImportError:

    import pyfits

logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("full_sky_simulation.py")
log.setLevel(logging.DEBUG)


def sanitize_filename(filename):

    return os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))


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

        # At the moment we only support source class
        assert irfs == "P8R2_SOURCE_V6", "At the moment we only support P8R2_SOURCE_V6"

        self._ft2 = sanitize_filename(ft2)
        self._tstart = tstart
        self._simulation_time = simulation_time
        self._irfs = irfs
        self._emin = emin
        self._emax = emax
        self._ltfrac = ltfrac

        # This will contain the list of temporary files produced
        self._temp_files = []

        self._simulated_ft1 = None

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
                          'infile': sanitize_filename(config.get("SLAC", "SIM_XML")),
                          'srclist': sanitize_filename(config.get("SLAC", "SIM_SRC_LIST")),
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

        log.info("About to start simulation")
        log.info("#### gtobsim output start #####")
        print("\n\n")

        gtobssim_app.run(**_gtobssim_args)

        print("\n\n")
        log.info("#### gtobsim output stop #####")

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

        log.info("Merging simulated event files")
        log.info("#### gtselect output start #####")
        print("\n\n")

        gtselect_app.run(infile=ft1_file_list, outfile=outfile,
                         ra=0.0, dec=0.0, rad=180.0,
                         tmin=self._tstart, tmax=self._tstart + self._simulation_time,
                         emin=self._emin, emax=self._emax,
                         zmax=180.0,
                         evclass=IRFS.IRFS[self._irfs].evclass,
                         evtype="INDEF",
                         convtype='-1')

        print("\n\n")
        log.info("#### gtselect output stop #####")

        # Now check how many events we had before gtselect
        n_simulated_events = 0

        for ft1 in event_files:

            with pyfits.open(ft1) as f:

                n_simulated_events += len(f['EVENTS'].data)

        # Now get the number of events which survived the cut
        n_simulated_events_after_cuts = 0

        with pyfits.open(outfile) as f:

            n_simulated_events_after_cuts += len(f['EVENTS'].data)

        assert n_simulated_events == n_simulated_events_after_cuts, "Some events were lost when cutting with gtselect!"

        log.info("Generated %s events of class %s" % (n_simulated_events_after_cuts, self._irfs))

        self._cleanup()

        # Store for future use
        self._simulated_ft1 = outfile

    def _track_temp_file(self, filename):

        self._temp_files.append(sanitize_filename(filename))

        return self._temp_files[-1]

    def _cleanup(self):

        for filename in self._temp_files:

            os.remove(filename)

    def _fix_galactic_diffuse_path(self, tree):

        # Find Galactic template in this system
        templ = findTemplate(IRFS.IRFS[self._irfs].galacticTemplate)

        # Now update the XML tree with the new location for the template

        # NOTE: this assume that the tree has been generated by gtburst

        src, = tree.findall("source[@name='GalacticTemplate']")

        src.findall("spatialModel")[0].set("file", templ)

    def _fix_isotropic_diffuse_path(self, tree):

        # Find Isotropic template in this system

        templ = findTemplate(IRFS.IRFS[self._irfs].isotropicTemplate)

        # Now update the XML tree with the new location for the template

        # NOTE: this assume that the tree has been generated by gtburst

        src, = tree.findall("source[@name='IsotropicTemplate']")

        src.findall("spectrum")[0].set("file", templ)

    def _fix_extended_sources_path(self, tree):

        # Get the data path for GtBurst, which contains the templates for the diffuse sources

        new_path = getDataPath()

        # Find all spatialModel tokens for the extended sources
        ext_sources = tree.findall("source/spatialModel[@file]")

        import pdb;pdb.set_trace()

        for spatial_model in ext_sources:

            file_path = spatial_model.get("file")

            if file_path.find("__FIXME__TEMPLATE_PATH") >= 0:

                spatial_model.set("file", file_path.replace("__FIXME__TEMPLATE_PATH", new_path))

    def run_gtdiffrsp(self):

        # Check that we have a simulated FT1

        assert self._simulated_ft1 is not None, "You have to run the simulation before computing the diffuse response"

        # Now get the full sky XML file, update the path of the Galactic and isotropic diffuse, and
        # copy it here to be used in gtdiffrsp
        orig_file_path = os.path.join(os.path.dirname(__file__), 'fullsky_xml_gtlike.xml')

        with open(orig_file_path, "r") as f:

            tree = ElementTree.parse(f)

        # Fix the path of the Galactic and isotropic template, as well as extended sources with FITS maps
        self._fix_galactic_diffuse_path(tree)
        self._fix_isotropic_diffuse_path(tree)
        self._fix_extended_sources_path(tree)

        # Write to a temporary file
        xml_file = self._track_temp_file("__gw_toolkit_xml.xml")

        with open(xml_file, "w+") as f:

            f.write(ElementTree.tostring(tree.getroot()))

        # Run gtdiffrsp

        gtdiffrsp_app = GtApp('gtdiffrsp')

        log.info("Computing diffuse response")
        log.info("#### gtdiffrsp output start #####")
        print("\n\n")

        gtdiffrsp_app.run(evfile=self._simulated_ft1, scfile=self._ft2,
                          srcmdl=xml_file,
                          irfs=self._irfs,
                          evclass=IRFS.IRFS[self._irfs].evclass,
                          convert="yes")

        print("\n\n")
        log.info("#### gtdiffrsp output stop #####")

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
