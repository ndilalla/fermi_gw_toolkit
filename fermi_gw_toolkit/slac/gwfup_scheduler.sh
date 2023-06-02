#!/bin/bash -e

export GPL_TASKROOT=/nfs/farm/g/glast/u26/GWFUP/

echo 'Sourcing the setup script'
source $GPL_TASKROOT/set_env/setup_ligo.sh

set -x
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/tools/gwfup_scheduler_kafka.py