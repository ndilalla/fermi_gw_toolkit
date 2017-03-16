#!/usr/bin/env python

########################################################
# Configuration
########################################################

SLAC_MAP_DIR = '/nfs/farm/g/glast/u26/GWPIPELINE/input/maps_from_Stanford'
SLAC_HOST = 'ftp.slac.stanford.edu'  # I use ftp just because it is not as loaded as rhel6-64


import logging
import sys, os
import argparse

from utils import fail_with_error, execute_command

logging.basicConfig(format='%(asctime)s %(message)s')
logging.info('submit_pipeline2_task is starting')

# Add the path where the Stanford data catalog is
sys.path.append('/storage/fermi-data/')


def get_maximum_available_MET():

    from myDataCatalog import DB

    db = DB.DB()

    c = db.query(''' select max(MET_stop) from FT1''')
    maxTimeLimit = c.fetchall()[0][0]

    return float(maxTimeLimit)



def submit_job(trigger_name, trigger_time, desired_tstart_met, desired_tstop_met, map_path):

    # Only submit the job if there is at least 1 ks of data after the trigger time

    if  get_maximum_available_MET() <= desired_tstart_met + 1000.0:

        # No available data
        fail_with_error(logging, "No data available yet")

    else:

        # Make sure map exists
        if not os.path.exists(map_path):

            fail_with_error(logging, "submit_job: map %s does not exists!" % map_path)

        # Move it to SLAC

        slac_path = "%s/%s_%s" % (SLAC_MAP_DIR, trigger_name, os.path.basename(map_path))

        cmd_line = 'rsync %s %s:%s' % (map_path, SLAC_HOST, slac_path)
        execute_command(logging, cmd_line)

        cmd_line = '/afs/slac.stanford.edu/u/gl/glast/pipeline-II/prod/pipeline createStream'

        cmd_line += ' GWFUP'

        cmd_line += ' --define TRIGGERNAME=%s' % trigger_name

        cmd_line += ' --define TRIGGERTIME=%s' % trigger_time

        cmd_line += ' --define TSTART=0' % desired_tstart_met
        cmd_line += ' --define TSTOP=%s' % desired_tstop_met

        cmd_line += ' --define HEALPIX_PATH_MAP=%s' % slac_path

        execute_command(logging, cmd_line)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='process_n_points')

    parser.add_argument('--triggername', required=True, type=str)
    parser.add_argument('--triggertime', required=True, type=float)
    parser.add_argument('--tstart', required=True, type=float)
    parser.add_argument('--tstop', required=True, type=float)
    parser.add_argument('--map', required=True, type=str)

    args = parser.parse_args()

    submit_job(args.trigger_name, args.trigger_time, args.tstart, args.tstop, args.map)
