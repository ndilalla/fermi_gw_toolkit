# This module contains a very specialized wrapper around pyLike that exploit the fact that we are using simulated
# data for the same ROI, so exposure map, livetime cube, diffuse models and so on are identical to the dataset
# we are simulating

import UnbinnedAnalysis
import pyLikelihood as pyLike


class FastUnbinnedObs(UnbinnedAnalysis.UnbinnedObs):
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


class FastTS(object):
    """
    A simple wrapper around the UnbinnedAnalysis machinery that avoid reloading the Galactic and Isotropic template,
    instead reusing the ones that have been already loaded.

    It can be used to quickly get the TS obtained with a simulated dataset where the simulation is identical to
    the original dataset, except for the FT1 file.

    """
    def __init__(self, orig_log_like, target_source="GRB"):

        self._orig_log_like = orig_log_like

        assert target_source in self._orig_log_like.sourceNames()

        self._target = target_source

    def _new_log_like(self, event_file):

        new_obs = FastUnbinnedObs(event_file, self._orig_log_like.observation)

        # Create empty XML to trick UnbinnedAnalysis in not reading up any source.
        # We will then add the source that have been already loaded in the original likelihood object.
        # This save 10-15 s because sources like the Galactic template do not need to be reloaded again from disk
        with open("__empty_xml.xml", "w+") as f:
            f.write('<source_library title="source library"></source_library>')

        # Load pyLike
        new_like = UnbinnedAnalysis.UnbinnedAnalysis(new_obs, "__empty_xml.xml", optimizer="Minuit")

        # Now load the sources from the other object
        for source_name in self._orig_log_like.sourceNames():

            new_like.addSource(self._orig_log_like.logLike.source(source_name))

        return new_like

    def get_TS(self, simulated_ft1):
        """
        Get the new TS for the target source using the simulated ft1 file

        :param simulated_ft1:
        :return:
        """

        new_like = self._new_log_like(simulated_ft1)

        new_like.optimize(verbosity=0)

        return new_like.Ts(self._target, reoptimize=True, approx=False)
