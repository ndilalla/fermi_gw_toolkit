#!/usr/bin/env python

# A wrapper to launch the task in the pipeline2 system at SLAC

from configuration import config
from utils import execute_command, fail_with_error
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
    execute_command(log, "chmod a+rwx --recursive %s" % this_trigger_input_dir)

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

    cmd_line += ' --define EMAX=1000'

    cmd_line += ' --define HEALPIX_MAP=%s' % args.map

    cmd_line += ' --define VERSION=%s' % version

    if simulate:

        cmd_line += " --define SIMULATE_MODE=1"

    try:

        execute_command(log, cmd_line)

    except:

        fail_with_error(log, "Could not execute %s. Traceback: \n\n %s" % (cmd_line, traceback.format_exc()))
