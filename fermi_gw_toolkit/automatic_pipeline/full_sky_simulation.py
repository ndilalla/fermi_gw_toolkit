import logging
import glob
import os
from configuration import config
import numpy as np
from xml.etree import ElementTree
import shutil

from GtApp import GtApp

from GtBurst import IRFS
from GtBurst.LikelihoodComponent import findTemplate
from GtBurst.getDataPath import getDataPath
from GtBurst.dataHandling import _makeDatasetsOutOfLATdata

from utils import sanitize_filename, within_directory

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

        with pyfits.open(outfile, mode='update') as f:

            n_simulated_events_after_cuts += len(f['EVENTS'].data)

            # Need to fix this because gtobssim writes "1", which is not an acceptable reprocessing
            # version for gtburst

            f[0].header['PROC_VER'] = 302

        assert n_simulated_events == n_simulated_events_after_cuts, "Some events were lost when cutting with gtselect!"

        log.info("Generated %s events of class %s" % (n_simulated_events_after_cuts, self._irfs))

        self._cleanup()

        # Store for future use with its absolute path
        self._simulated_ft1 = sanitize_filename(outfile)

    def _track_temp_file(self, filename):

        self._temp_files.append(sanitize_filename(filename))

        return self._temp_files[-1]

    def _cleanup(self):

        for filename in self._temp_files:

            os.remove(filename)

        self._temp_files = []

    def _fix_galactic_diffuse_path(self, tree):

        # Find Galactic template in this system
        # If we are at slac, force the use of the same templates that have been simulated
        slac_simulated_templates_path = config.get("SLAC", "SIM_DIFFUSE_PATH")

        if os.path.exists(slac_simulated_templates_path):

            log.info("Forcing the use of templates in directory %s" % slac_simulated_templates_path)

            os.environ['GTBURST_TEMPLATE_PATH'] = config.get("SLAC", "SIM_DIFFUSE_PATH")

        templ = findTemplate(IRFS.IRFS[self._irfs].galacticTemplate)

        # Now update the XML tree with the new location for the template

        # NOTE: this assume that the tree has been generated by gtburst

        src, = tree.findall("source[@name='GalacticTemplate']")

        src.findall("spatialModel")[0].set("file", templ)

    def _fix_isotropic_diffuse_path(self, tree):

        # Find Isotropic template in this system
        # If we are at slac, force the use of the same templates that have been simulated
        slac_simulated_templates_path = config.get("SLAC", "SIM_DIFFUSE_PATH")

        if os.path.exists(slac_simulated_templates_path):

            log.info("Forcing the use of templates in directory %s" % slac_simulated_templates_path)

            os.environ['GTBURST_TEMPLATE_PATH'] = config.get("SLAC", "SIM_DIFFUSE_PATH")

        templ = findTemplate(IRFS.IRFS[self._irfs].isotropicTemplate)

        # Now update the XML tree with the new location for the template

        # NOTE: this assume that the tree has been generated by gtburst

        src, = tree.findall("source[@name='IsotropicTemplate']")

        src.findall("spectrum")[0].set("file", templ)

    # def _fix_extended_sources_path(self, tree):
    #
    #     # Get the data path for GtBurst, which contains the templates for the diffuse sources
    #
    #     new_path = os.path.join(getDataPath(), "templates")
    #
    #     # Find all spatialModel tokens for the extended sources
    #     ext_sources = tree.findall("source/spatialModel[@file]")
    #
    #     for spatial_model in ext_sources:
    #
    #         file_path = spatial_model.get("file")
    #
    #         if file_path.find("__FIXME__TEMPLATE_PATH") >= 0:
    #
    #             spatial_model.set("file", file_path.replace("__FIXME__TEMPLATE_PATH", new_path))

    def run_gtdiffrsp(self):

        # Check that we have a simulated FT1

        assert self._simulated_ft1 is not None, "You have to run the simulation before computing the diffuse response"

        # Now get the full sky XML file, update the path of the Galactic and isotropic diffuse, and
        # copy it here to be used in gtdiffrsp
        orig_file_path = os.path.join(os.path.dirname(__file__), 'fullsky_xml_gtlike.xml')

        with open(orig_file_path, "r") as f:

            tree = ElementTree.parse(f)

        # Fix the path of the Galactic and isotropic template
        self._fix_galactic_diffuse_path(tree)
        self._fix_isotropic_diffuse_path(tree)

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
                          convert="yes")

        print("\n\n")
        log.info("#### gtdiffrsp output stop #####")

        self._cleanup()

    def make_data_package_files(self, trigger_name, ra=0.0, dec=0.0, trigger_time=None, destination_dir='.'):
        """
        Make data package for gtburst

        :return:
        """

        if trigger_time is None:

            trigger_time = self._tstart

        destination_dir = sanitize_filename(destination_dir)

        with within_directory(destination_dir, create=True):

            # Rename ft1 and ft2
            new_ft1 = 'gll_ft1_tr_bn%s_v00.fit' % trigger_name.replace("bn","")
            new_ft2 = 'gll_ft2_tr_bn%s_v00.fit' % trigger_name.replace("bn","")

            shutil.copy(self._simulated_ft1, new_ft1)
            shutil.copy(self._ft2, new_ft2)

            _makeDatasetsOutOfLATdata(new_ft1,
                                      new_ft2,
                                      trigger_name, self._tstart, self._tstart + self._simulation_time,
                                      ra, dec, trigger_time,
                                      localRepository=".",
                                      cspecstart=0, cspecstop=10)

        # Remove all other files
        self._cleanup()

        os.remove(self._simulated_ft1)
        self._simulated_ft1 = None