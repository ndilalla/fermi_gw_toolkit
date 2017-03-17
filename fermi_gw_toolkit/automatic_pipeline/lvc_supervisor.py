#!/usr/bin/env python

import glob
import os
import sys
import logging
import subprocess
from configuration import config
from utils import execute_command, send_notice, fail_with_error

logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("lvc_supervisor")
log.setLevel(logging.DEBUG)
log.info('lvc_supervisor is starting')


# This script is run by cron

if __name__ == "__main__":

    # First find out if there are maps in the Mail directory (which is where procmail puts them)

    maps = glob.glob(os.path.join(os.path.expanduser("~"), 'Mail', '*_gwmap_*'))

    if len(maps) == 0:

        log.info("Found no map to be processed")

        # Nothing to do
        sys.exit(0)

    else:

        log.info("Found %s maps" % (len(maps)))

    # Create list of unique triggers to be processed

    triggers = set(map(lambda x: os.path.basename(x).split("_gwmap")[0], maps))

    log.info("Found %i unique triggers" % len(triggers))

    for trigger in triggers:

        log.info("Processing trigger %s" % trigger)

        # 99.9% of the time this will be a loop of 1, as it is very unlikely that two triggers will be waiting to
        # be executed at the same time

        # Find all maps referring to this trigger
        this_maps = filter(lambda x: os.path.basename(x).find(trigger) == 0, maps)

        assert len(this_maps) > 0, "No maps for trigger %s (this should be impossible)" % trigger

        # Find the most recent map for this trigger
        most_recent_map = max(this_maps, key=os.path.getctime)

        log.info("Most recent map found is %s" % most_recent_map)

        # Submit job for this map
        cmd_line = "python "

        cmd_line += os.path.join(config.get("Stanford", "FERMI_GW_TOOLKIT_PATH"), 'fermi_gw_toolkit',
                                'automatic_pipeline', 'submit_pipeline2_task.py')

        cmd_line += " --tstop 10000"

        cmd_line += " --map %s" % most_recent_map

        if config.getboolean("Stanford", "SIMULATE"):

            cmd_line += " --simulate"

        try:

            execute_command(log, cmd_line)

        except subprocess.CalledProcessError as grepexc:

            if grepexc.returncode == -10:

                # No data

                log.error("submit_pipeline2_task.py failed, probably no data is available for this trigger")

                continue

            else:

                # This is an uncaught error
                fail_with_error(log, "Failed in an unexpected way")

        else:

            text = "Submitted job for trigger %s with map %s" % (trigger, most_recent_map)

            log.info(text)

            send_notice("LVC: submitted %s" % trigger, text)

            # Move all the maps for this trigger away so we don't re-process them
            for map in this_maps:

                dest = os.path.join(config.get("Stanford", "USED_MAP_DIR"), os.path.basename(map))

                log.debug("Moving %s to %s" % (map, dest))

                os.rename(map, dest)

            # We are done for this trigger
            continue


