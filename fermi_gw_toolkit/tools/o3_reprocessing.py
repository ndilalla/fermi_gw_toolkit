#!/usr/bin/env python2.7
import argparse
import os
import numpy

from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.tools.ScanEvents import get_info

EVENT_LIST_FILE = GPL_TASKROOT + '/databases/O3_event_list.txt'
HISTORY_FILE = GPL_TASKROOT + '/databases/O3_history.txt'

__description__='Script to launch the O3 reprocessing'
formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)
parser.add_argument("-n", help="Event number", type=int, required=False, 
                    default=None, choices=range(1, 57))
parser.add_argument('--history', type=int, required=False, choices=[0, 1], default=1)
args = parser.parse_args()

evt_numbers, evt_names = numpy.loadtxt(EVENT_LIST_FILE, dtype=str, unpack=True)
his_numbers, his_names = numpy.loadtxt(HISTORY_FILE, dtype=str, unpack=True)

if args.n is None:
    print("No event number provided. Reading from history file %s..." % HISTORY_FILE)
    last_n = his_numbers[-1]
    last_names = his_names[-1]
    print("Last processed event was %s (n.%s)" % (last_names, last_n))
    new_n = int(last_n) + 1
else:
    new_n = args.n

repro_name = evt_names[new_n - 1]
print('Reprocessing evt %s (n.%s)...' % (repro_name, new_n))

info = get_info(repro_name)

skymap = info['skymap_fits']
print('Using skymap %s...' % skymap)

cmd = 'python %s/tools/submit_gwfup_job.py --url %s --nside 64 --version v01 --run_bayul 1 --pixels_job 5 --wall_time 4' % (FERMI_GW_ROOT, skymap)
print(cmd)

os.system(cmd)

if args.history == 1:
    print("Updating history file..")
    with open(HISTORY_FILE, "a") as f:
        f.write("%d\t%s\n" % (new_n, repro_name))

print("Done")
