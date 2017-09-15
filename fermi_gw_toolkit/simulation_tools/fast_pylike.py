# This module contains a very specialized wrapper around pyLike that exploit the fact that we are using simulated
# data for the same ROI, so exposure map, livetime cube, diffuse models and so on are identical to the dataset
# we are simulating

import os
import shutil
import glob
import logging
import subprocess
import time, datetime
import numpy as np

import astropy.io.fits as pyfits
from fermi_gw_toolkit.automatic_pipeline.utils import within_directory, execute_command, sanitize_filename
from fast_ts_map import FastTSMap
from setup_ftools import setup_ftools_non_interactive

import UnbinnedAnalysis
import pyLikelihood as pyLike
from GtApp import GtApp



# Configure logger
logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("fast_pylike.py")
log.setLevel(logging.DEBUG)

# Setup FTOOLS to be non-interactive
setup_ftools_non_interactive()


# The pyLikelihood code contains a statement where scData are emptied after the observation has been set up
# We want to avoid that, so we can reuse those data without reading them over and over again
# therefore we override only that part
class MyUnbinnedObs(UnbinnedAnalysis.UnbinnedObs):

    def _readData(self, scFile, eventFile):

        self._readScData(scFile, eventFile)
        self._readEvents(eventFile)

        # This part is in the pyLikelihood code, but we actually want to keep the scData in memory
        # so we can reuse them!

        # if self.expCube is not None and self.expCube != "":
        #     # Clear the spacecraft data to save memory for long observations.
        #     self._scData.clear_arrays()


class FastUnbinnedObs(MyUnbinnedObs):
    """
    A simple wrapper around UnbinnedAnalysis.UnbinnedObs that avoid reloading the livetime cube and the exposure map,
    and instead reuse the one that have been already loaded in RAM in the original pyLikelihood object

    """
    def __init__(self, new_event_file, other_obs):
        self.sctable = other_obs.sctable

        self.checkCuts = False

        self.expMap = other_obs.expMap
        self.expCube = other_obs.expCube
        self.irfs = other_obs.irfs
        ft2 = other_obs.scFiles[0]

        self._inputs = '\n'.join(('Event file(s): ' + str(new_event_file),
                                  'Spacecraft file(s): ' + str(ft2),
                                  'Exposure map: ' + str(self.expMap),
                                  'Exposure cube: ' + str(self.expCube),
                                  'IRFs: ' + str(self.irfs)))

        self._respFuncs = other_obs._respFuncs

        self._expMap = other_obs._expMap

        self._scData = other_obs._scData

        self._roiCuts = other_obs._roiCuts

        self._expCube = other_obs._expCube

        self._eventCont = pyLike.EventContainer(self._respFuncs, self._roiCuts,
                                                self._scData)
        self.observation = pyLike.Observation(self._respFuncs, self._scData,
                                              self._roiCuts, self._expCube,
                                              self._expMap, self._eventCont)
        self._readData(ft2, new_event_file)

    # Override these with faster versions, which avoid to re-read data that have been already read

    def _readEvents(self, eventFile):

        if eventFile is not None:
            eventFiles = self._fileList(eventFile)

            # This has been already read

            #self._roiCuts.readCuts(eventFiles, 'EVENTS', False)

            for file in eventFiles:

                self._eventCont.getEvents(file)

            self.eventFiles = eventFiles

    def _readScData(self, scFile, eventFile):

        # This is useless (it has been already read)

        # if eventFile is not None:
        #     eventFiles = self._fileList(eventFile)
        #     self._roiCuts.readCuts(eventFiles, 'EVENTS', False)

        # tmin = self._roiCuts.minTime()
        # tmax = self._roiCuts.maxTime()
        scFiles = self._fileList(scFile)

        # This has been already read
        #self._scData.readData(scFiles, tmin, tmax, self.sctable)

        self.scFiles = scFiles


class SimulationFeeder(object):

    def __init__(self, ft1, ft2, expmap, ltcube, xml_file, path_of_tar_file_with_simulated_ft1_files,
                 tsmap_spec=None, srcname='GRB'):

        # Process the simulations applying the same cuts as in the data file
        sp = SimulationProcessor(ft1, ft2, path_of_tar_file_with_simulated_ft1_files)

        ra_center, dec_center, radius = sp.roi

        # Now create the likelihood object
        obs = MyUnbinnedObs(ft1, ft2, expMap=expmap, expCube=ltcube)
        like = UnbinnedAnalysis.UnbinnedAnalysis(obs, xml_file, "MINUIT")

        fast_ts = FastTS(like, ts_map_spec=tsmap_spec, target_source=srcname)

        # Get the TSs
        self._tss = fast_ts.process_ft1s(sp.processed_ft1s, ra_center=ra_center, dec_center=dec_center)

    @property
    def TSs(self):

        return self._tss

    def write(self, filename):
        """
        Write TSs to disk in the given filename (with .npy extension)

        :param filename:
        :return:
        """

        np.save(filename, self.TSs)


class SimulationProcessor(object):

    def __init__(self, original_ft1, original_ft2, path_of_tar_file_with_simulated_ft1_files, workdir="simulated_ft1s"):

        # Make absolute path and resolve env. variables (if any)

        original_ft1 = sanitize_filename(original_ft1)
        original_ft2 = sanitize_filename(original_ft2)  # This is needed only if we want to switch back to gtmktime
        path_of_tar_file_with_simulated_ft1_files = sanitize_filename(path_of_tar_file_with_simulated_ft1_files)

        # Read from the original FT1 the cuts
        roi_cuts = pyLike.RoiCuts()
        roi_cuts.readCuts(original_ft1)

        # ROI definition

        ra_center, dec_center, radius = roi_cuts.roiCone()

        # Store them as well
        self._ra_center = ra_center
        self._dec_center = dec_center
        self._radius = radius

        # Energy minimum and maximum
        emin, emax = roi_cuts.getEnergyCuts()

        with pyfits.open(original_ft1) as f:

            tstart = f['EVENTS'].header['TSTART']
            tstop = f['EVENTS'].header['TSTOP']

        # Unpack tar file here
        with within_directory(workdir, create=True):

            # Copy tar here, unpack, then remove copy
            log.info("Copying %s to %s..." % (path_of_tar_file_with_simulated_ft1_files, workdir))
            shutil.copy2(path_of_tar_file_with_simulated_ft1_files, ".")

            execute_command(log, "tar zxf %s" % path_of_tar_file_with_simulated_ft1_files)

            os.remove(os.path.basename(path_of_tar_file_with_simulated_ft1_files))

            # Now get the names of all ft1s
            all_ft1s_raw = glob.glob("gll_ft1_tr_bn*_v00.fit")

            log.info("Found %s simulated FT1 files in archive %s" % (len(all_ft1s_raw),
                                                                     path_of_tar_file_with_simulated_ft1_files))

            log.info("Filtering them with the same cuts as in %s" % (original_ft1))

            self._all_ft1s = []

            # Apply the cuts to them
            for i, this_simulated_ft1 in enumerate(all_ft1s_raw):

                if (i+1) % 100 == 0:

                    log.info("Processed %i of %i" % (i+1, len(all_ft1s_raw)))

                # temp_file1 = "__temp_ft1.fit"
                #
                # self.gtmktime_from_file(original_ft1, original_ft2, this_simulated_ft1, temp_file1)
                #
                # temp_file2 = "__temp_ft1_2.fit"
                #
                # self.gtselect(ra_center, dec_center, radius, tstart, tstop, emin, emax, temp_file1, temp_file2)
                #
                # os.remove(temp_file1)
                #
                basename = os.path.splitext(os.path.basename(this_simulated_ft1))[0]

                new_name = "%s_filt.fit" % basename

                self._filter_simulated_ft1(original_ft1, this_simulated_ft1,
                                           ra_center, dec_center, radius,
                                           tstart, tstop,
                                           emin, emax,
                                           new_name)

                # os.rename(temp_file2, new_name)

                self._all_ft1s.append(sanitize_filename(new_name))

                # Remove the simulated FT1 to save space

                os.remove(this_simulated_ft1)

    @property
    def roi(self):

        return (self._ra_center, self._dec_center, self._radius)

    @property
    def processed_ft1s(self):

        return self._all_ft1s

    @staticmethod
    def _filter_simulated_ft1(original_ft1, simulated_ft1,
                              ra, dec, radius, tmin, tmax, emin, emax, outfile):
        """
        This accomplish what gtselect and gtmktime would do, but in one single command (much faster). This is possible
        again because we are applying GTIs that are already known.

        :param original_ft1:
        :param simulated_ft1:
        :param ra:
        :param dec:
        :param radius:
        :param tmin:
        :param tmax:
        :param emin:
        :param emax:
        :param outfile:
        :return:
        """

        # Now filter

        my_filter = 'gtifilter("%s") && ANGSEP(RA, DEC, %s, %s) <= %s ' \
                    '&& TIME>=%s && TIME<=%s && ENERGY >=%s && ENERGY <=%s' % (original_ft1, ra, dec, radius,
                                                                               tmin, tmax, emin, emax)

        cmd_line = "ftcopy '%s[EVENTS][%s]' %s copyall=yes clobber=yes history=yes" % (simulated_ft1,
                                                                                       my_filter, outfile)

        subprocess.check_call(cmd_line, shell=True)

        # Now update the DS keywords from the orginal file, so that downstream software will understand
        # the file even though we didn't use gtselect nor gtmktime

        with pyfits.open(sanitize_filename(original_ft1)) as orig:

            with pyfits.open(outfile, mode='update') as new:

                # Copy keywords from original file
                orig_header = orig['EVENTS'].header
                relevant_keywords = filter(lambda x:x.find("DS")==0 or x == "NDSKEYS", orig['EVENTS'].header.keys())

                for keyword in relevant_keywords:

                    new['EVENTS'].header[keyword] = orig_header[keyword]


    @staticmethod
    def gtselect(ra_center, dec_center, radius, tmin, tmax, emin, emax, simulated_ft1, output_ft1):

        # NOTE: we assume there is no need for a Zenith cut, because the Zenith cut has been made with
        # gtmktime
        gtselect = GtApp('gtselect')

        gtselect.run(print_command=False,
                     infile=sanitize_filename(simulated_ft1),
                     outfile=output_ft1,
                     ra=ra_center,
                     dec=dec_center,
                     rad=radius,
                     tmin=tmin,
                     tmax=tmax,
                     emin=emin,
                     emax=emax,
                     zmin=0,
                     zmax=180, # Zenith cut must be applied with gtmktime
                     evclass="INDEF",  # Assume simulation has been made with the same evclass of the input file
                     evtype='INDEF')

    @staticmethod
    def gtmktime_from_file(original_ft1, original_ft2, simulated_ft1, output_ft1):
        """

        :param original_ft1:
        :param original_ft2:
        :param simulated_ft1:
        :param output_ft1:
        :return:
        """

        # Add the GTI extension to the data file
        with pyfits.open(sanitize_filename(original_ft1)) as orig:

            with pyfits.open(simulated_ft1, mode='update') as new:

                # Copy the GTIs from the original file

                new['GTI'] = orig['GTI']

                # Re-write header info (inaccuracy due to pil conversion float to str)
                for ehdu, ghdu in zip(new, orig):
                    ehdu.header['TSTART'] = ghdu.header['TSTART']
                    ehdu.header['TSTOP'] = ghdu.header['TSTOP']

        # Now run gtmktime which will update the headers and select the events based on the GTIs

        gtmktime = GtApp('gtmktime')

        gtmktime.run(print_command=False,
                     evfile=simulated_ft1,
                     outfile=output_ft1,
                     scfile=original_ft2,
                     filter='T',  # This filter is always true, which means we are not adding any new filter
                     roicut='no',
                     apply_filter='yes'  # This will make gtmktime cut on the GTIs
                     )


class FastTS(object):
    """
    A simple wrapper around the UnbinnedAnalysis machinery that avoid reloading the Galactic and Isotropic template,
    instead reusing the ones that have been already loaded.

    It can be used to quickly get the TS obtained with a simulated dataset where the simulation is identical to
    the original dataset, except for the FT1 file.

    """
    def __init__(self, orig_log_like, ts_map_spec=None, target_source="GRB", optimizer="MINUIT"):

        # Store original likelihood object

        self._orig_log_like = orig_log_like

        # Make sure the target is contained in the likelihood object

        assert target_source in self._orig_log_like.sourceNames()

        # Store target

        self._target = target_source

        # Store TS map specification
        self._tsmap_spec = ts_map_spec

        # Store optimizer
        self._optimizer = optimizer

    def _new_log_like(self, event_file):

        new_obs = FastUnbinnedObs(event_file, self._orig_log_like.observation)

        # Create empty XML to trick UnbinnedAnalysis in not reading up any source.
        # We will then add the source that have been already loaded in the original likelihood object.
        # This saves a lot because sources like the Galactic template do not need to be reloaded again from disk
        with open("__empty_xml.xml", "w+") as f:
            f.write('<source_library title="source library"></source_library>')

        # Load pyLike (we use DRMNFB because it is fast, much faster than Minuit, and we do not care about the errors)
        new_like = UnbinnedAnalysis.UnbinnedAnalysis(new_obs, "__empty_xml.xml",
                                                     optimizer=self._optimizer)

        # Now load the sources from the other object
        for source_name in self._orig_log_like.sourceNames():

            if source_name[-1] == 'e' and source_name.find("Template") < 0:

                # Extended source, jump it (we didn't compute gtdiffrsp because it crashes)
                continue

            new_like.addSource(self._orig_log_like.logLike.source(source_name))

        return new_like

    def get_TS(self, simulated_ft1, ra_center=None, dec_center=None, test_source=None):
        """
        Get the new TS for the target source using the simulated ft1 file

        :param simulated_ft1:
        :param ra_center:
        :param dec_center:
        :return:
        """

        new_like = self._new_log_like(simulated_ft1)

        if self._tsmap_spec is not None:

            assert ra_center is not None and dec_center is not None, "If you use the TS map you have to provide " \
                                                                     "ra_center and dec_center"

            # Need to do a quick TS map

            half_size, n_side = self._tsmap_spec.replace(" ", "").split(",")

            half_size = float(half_size)
            n_side = int(n_side)

            ftm = FastTSMap(new_like, test_source=test_source)
            _, this_TS = ftm.search_for_maximum(ra_center, dec_center,
                                                half_size, n_side,
                                                verbose=False)

        else:

            new_like.optimize(verbosity=0)

            this_TS = new_like.Ts(self._target, reoptimize=True, approx=False)

        return this_TS

    def process_ft1s(self, ft1s, ra_center, dec_center):

        # Get the TSs
        tss = np.zeros(len(ft1s))

        log.info("Computing TSs...")

        start_time = time.time()

        # Create a test source outside of the loop, so the exposure is computed only here (and not for every
        # ft1 file). This can be done because all ft1s are assumed to be a simulation of the
        # same ROI in the same interval, so they share the same livetime cube and exposure map

        test_source = pyLike.PointSource(ra_center, dec_center, self._orig_log_like.logLike.observation())
        test_source.setSpectrum(self._orig_log_like[self._target].spectrum().clone())
        test_source.setName("_test_source")

        for i, ft1 in enumerate(ft1s):

            tss[i] = self.get_TS(ft1, ra_center, dec_center, test_source=test_source)

            if (i+1) % 100 == 0:

                this_time = time.time()
                elapsed_time = (this_time - start_time)
                time_per_ts = elapsed_time / (i+1)
                remaining_time = (len(ft1s) - (i+1)) * time_per_ts

                log.info("Processed %i out of %i" % (i + 1, len(ft1s)))
                log.info("Elapsed time: %s, remaining time: %s" % (datetime.timedelta(seconds=elapsed_time),
                                                                   datetime.timedelta(seconds=remaining_time)))

        log.info("done")

        return tss
