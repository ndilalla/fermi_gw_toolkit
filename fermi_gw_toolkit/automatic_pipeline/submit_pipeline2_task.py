#!/usr/bin/env python

from GtBurst.dataHandling import date2met

import logging
import sys, os
import argparse
import traceback
from configuration import config
from utils import fail_with_error, execute_command

try:

    import astropy.io.fits as pyfits

except ImportError:

    import pyfits

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

        slac_path = "%s/%s_%s" % (config.get("SLAC", "MAP_DIR"), trigger_name, os.path.basename(map_path))

        cmd_line = 'rsync %s %s:%s' % (map_path, config.get("SLAC","SSH_HOST"), slac_path)

        execute_command(log, cmd_line)

        # Now submit the job at SLAC using ssh

        cmd_line = 'ssh %s' % config.get("SLAC","SSH_HOST")

        command = os.path.join(config.get("SLAC","FERMI_GW_TOOLKIT_PATH"), 'fermi_gw_toolkit', 'automatic_pipeline',
                               'p2_task_wrapper.py')

        cmd_line += ' python %s' % command

        cmd_line += ' --triggername %s' % trigger_name

        cmd_line += ' --triggertime %s' % trigger_time

        cmd_line += ' --tstart_met %s' % desired_tstart_met
        cmd_line += ' --tstop_met %s' % desired_tstop_met

        cmd_line += ' --map %s' % slac_path

        if simulate:

            cmd_line += " --simulate"

        try:

            execute_command(log, cmd_line)

        except:

            fail_with_error(log, "Could not execute %s. Traceback: \n\n %s" % (cmd_line, traceback.format_exc()))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='submit_pipeline2_task')

    parser.add_argument('--tstop', required=True, type=float,
                        help='Stop of the time interval for the analysis, in time since the trigger')
    parser.add_argument('--map', required=True, type=str)
    parser.add_argument('--simulate', action='store_true')

    args = parser.parse_args()

    if args.simulate:

        simulate = True

    else:

        simulate = False

    # Read from the map trigger name and the UTC date and time
    with pyfits.open(args.map) as f:

        # We add bn otherwise some tools might get confused

        triggername = "bn%s" % f[1].header['OBJECT']

        trigger_date = f[1].header.get("DATE-OBS")

    # Now transform the trigger_date in the triggertime (in MET)
    triggertime = date2met(trigger_date.replace("T"," "))

    tstart_met = triggertime
    tstop_met = triggertime + args.tstop
    # Transform the trigger

    submit_job(triggername, triggertime, tstart_met, tstop_met, args.map, simulate=simulate)
