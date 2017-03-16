#!/usr/bin/env python

########################################################
# Configuration
########################################################

SLAC_MAP_DIR = '/nfs/farm/g/glast/u26/GWPIPELINE/input/maps_from_Stanford'
SLAC_HOST = 'ftp.slac.stanford.edu'  # I use ftp just because it is not as loaded as rhel6-64


import logging
import sys, os
import argparse
import traceback

from utils import fail_with_error, execute_command

logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("submit_pipeline2")
log.setLevel(logging.DEBUG)
log.info('submit_pipeline2_task is starting')

# Add the path where the Stanford data catalog is
sys.path.append('/storage/fermi-data/')


def get_maximum_available_MET():

    from myDataCatalog import DB

    db = DB.DB()

    c = db.query(''' select max(MET_stop) from FT1''')
    maxTimeLimit = c.fetchall()[0][0]

    return float(maxTimeLimit)


def submit_job(trigger_name, trigger_time, desired_tstart_met, desired_tstop_met, map_path, simulate=False):

    # Only submit the job if there is at least 1 ks of data after the trigger time

    if  get_maximum_available_MET() <= desired_tstart_met + 1000.0:

        # No available data
        fail_with_error(log, "No data available yet")

    else:

        # Make sure map exists
        if not os.path.exists(map_path):

            fail_with_error(log, "submit_job: map %s does not exists!" % map_path)

        # Move it to SLAC

        slac_path = "%s/%s_%s" % (SLAC_MAP_DIR, trigger_name, os.path.basename(map_path))

        cmd_line = 'rsync %s %s:%s' % (map_path, SLAC_HOST, slac_path)

        execute_command(log, cmd_line)

        # Now submit the job at SLAC using ssh

        cmd_line = 'ssh %s' % SLAC_HOST

        cmd_line += ' echo /afs/slac.stanford.edu/u/gl/glast/pipeline-II/prod/pipeline createStream'

        cmd_line += ' GWFUP'

        cmd_line += ' --define TRIGGERNAME=%s' % trigger_name

        cmd_line += ' --define TRIGGERTIME=%s' % trigger_time

        cmd_line += ' --define TSTART=%s' % desired_tstart_met
        cmd_line += ' --define TSTOP=%s' % desired_tstop_met

        cmd_line += ' --define HEALPIX_PATH_MAP=%s' % slac_path

        if simulate:

            cmd_line += " --define SIMULATE_MODE=1"

        try:

            execute_command(log, cmd_line)

        except:

            fail_with_error(log, "Could not execute %s. Traceback: \n\n %s" % (cmd_line, traceback.format_exc()))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='process_n_points')

    parser.add_argument('--triggername', required=True, type=str)
    parser.add_argument('--triggertime', required=True, type=float)
    parser.add_argument('--tstart', required=True, type=float)
    parser.add_argument('--tstop', required=True, type=float)
    parser.add_argument('--map', required=True, type=str)
    parser.add_argument('--simulate', action='store_true')

    args = parser.parse_args()

    if args.simulate:

        simulate = True

    else:

        simulate = False

    submit_job(args.triggername, args.triggertime, args.tstart, args.tstop, args.map, simulate=simulate)