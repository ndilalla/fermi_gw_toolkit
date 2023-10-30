#!/bin/bash -e

export GPL_TASKROOT=/sdf/data/fermi/n/u26/GWFUP/
source $GPL_TASKROOT/set_env/setup_ligo.sh

echo "Running on $(hostname) machine with pid $$"

set -x
python -u $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/tools/gwfup_scheduler_kafka.py