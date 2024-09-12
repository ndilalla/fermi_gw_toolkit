#!/bin/bash -e

export GPL_TASKROOT=/sdf/data/fermi/n/u26/GWFUP/
export DONE_DIR=$GPL_TASKROOT/status/done/
date

if [ "$(ls -A $DONE_DIR)" ]; then
    echo "New events found in $DONE_DIR"
    ls $DONE_DIR

    echo 'Sourcing the setup script'
    source $GPL_TASKROOT/set_env/setup_gwfup.sh

    set -x
    python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/bin/copy_events.py --directory ${DONE_DIR} --send_alert True
else
    echo "$DONE_DIR is empty"
fi
