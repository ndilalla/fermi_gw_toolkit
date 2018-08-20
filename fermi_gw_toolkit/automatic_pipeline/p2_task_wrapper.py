#!/usr/bin/env python

# A wrapper to launch the task in the pipeline2 system at SLAC

from configuration import config
from utils import execute_command, fail_with_error, sanitize_filename
import argparse
import logging
import traceback
import os
import glob

logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("p2_task_wrapper")
log.setLevel(logging.DEBUG)
log.info('p2_task_wrapper is starting')


if __name__ == "__main__":

    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description="Wrapper around the pipeline2 task, to be run at SLAC",
                                     formatter_class=formatter)

    parser.add_argument('--triggertime', help='Trigger time',
                        type=float, required=True)
    parser.add_argument('--triggername', type=str, required=True,
                        help='Name of the GW trigger')
    parser.add_argument('--tstart_met', type=float, required=True,
                        help='Start time for the analysis (in MET)')
    parser.add_argument('--tstop_met', help='Stop time for the analysis (in MET)',
                        type=float, required=True)
    parser.add_argument('--map', help='Path to local HEALPIX map',
                        type=str, required=True)
    parser.add_argument('--simulate', action='store_true')

    parser.add_argument('--sim_ft1_tar', help="Path to .tar file containing simulated FT1 data (full sky)", type=str,
                        required=False, default=None)

    parser.add_argument('--ligo_coverage_cl', help="How much of the LIGO map should we cover? "
                                                   "Use 0.9 to cover the 90% contour, for example. Default: 0.9",
                        default=0.9, type=float)

    parser.add_argument('--irfs', help="IRF to use. Default: p8_transient010e",
                        default="p8_transient010e", choices=['p8_transient020', 'p8_transient020e',
                                                             'p8_transient010', 'p8_transient010e',
                                                             'p8_source', 'p8_clean', 'p8_ultraclean'])

    args = parser.parse_args()

    if args.simulate:

        simulate = True

    else:

        simulate = False

    # Make sure that the trigger name starts with bn (otherwise doTimeResolvedLike, used by many scripts, might
    # get confused)

    if not args.triggername.find("bn") == 0:

        # Need to add "bn" at the beginning

        triggername = "bn%s" % args.triggername

    else:

        # "bn" is already present

        triggername = args.triggername

    # First we need to figure out the version, i.e., if a task for this GW event has been already run
    # This will be something like /nfs/farm/g/glast/u26/GWPIPELINE/input/bnGW150914

    this_trigger_input_dir = os.path.join(config.get("SLAC", "INPUT_DIR"), triggername)

    # Find existing existing_versions
    existing_versions = glob.glob(os.path.join(this_trigger_input_dir, 'v*'))

    if len(existing_versions) == 0:

        # There are no existing existing_versions
        version = 'v00'

    else:

        # Remove absolute path
        existing_versions = map(os.path.basename, existing_versions)

        # Find the last existing version
        existing_versions.sort()

        last_existing_version = existing_versions[-1]

        # Make the new version string
        version = "v%02i" % (int(last_existing_version.replace("v", "")) + 1)

    # Now create the directory

    dir_path = os.path.join(this_trigger_input_dir, version)

    os.makedirs(dir_path)

    # Change directory permission to rw-rw-rw-
    #os.chmod(dir_path, 0o666)
    # Make sure all files and directories have the right permissions
    try:

        execute_command(log, "chmod a+rwx --recursive %s" % this_trigger_input_dir)

    except:

        log.error("Could not change all permissions")

    map_path = sanitize_filename(args.map)

    assert os.path.exists(map_path), "The map %s does not exist" % map_path

    # Finally run the stream

    # P2_EXE is the path to the executable, likely /afs/slac.stanford.edu/u/gl/glast/pipeline-II/prod/pipeline

    cmd_line = '%s createStream' % config.get('SLAC', 'P2_EXE')

    cmd_line += ' %s' % config.get('SLAC', 'P2_TASK')

    cmd_line += ' --define TRIGGERNAME=%s' % triggername

    cmd_line += ' --define TRIGGERTIME=%s' % args.triggertime

    cmd_line += ' --define MET_TSTART=%s' % args.tstart_met
    cmd_line += ' --define MET_TSTOP=%s' % args.tstop_met

    cmd_line += ' --define MET_FT2TSTART=%s' % (args.tstart_met - 10000.0)
    cmd_line += ' --define MET_FT2TSTOP=%s' % (args.tstop_met + 10000.0)

    cmd_line += ' --define EMAX=100000'

    cmd_line += ' --define HEALPIX_PATH=%s' % map_path

    cmd_line += ' --define VERSION=%s' % version

    cmd_line += ' --define LIGO_COVERAGE_CL=%s' % args.ligo_coverage_cl

    cmd_line += ' --define IRFS=%s' % args.irfs

    if simulate:

        cmd_line += " --define SIMULATE_MODE=1"

    # If there is a tar file provided, pass it on to the pipeline for analyzing the simulated FT1 files within
    # the .tar
    if args.sim_ft1_tar is not None and args.sim_ft1_tar is not "none":

        tar_path = sanitize_filename(args.sim_ft1_tar)

        assert os.path.exists(tar_path), "The tar file %s does not exist" % tar_path

        cmd_line += ' --define SIMULATE_ROI_TARFILE=%s' % tar_path

    try:

        execute_command(log, cmd_line)

    except:

        fail_with_error(log, "Could not execute %s. Traceback: \n\n %s" % (cmd_line, traceback.format_exc()))
