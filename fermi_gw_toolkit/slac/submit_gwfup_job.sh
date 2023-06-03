#!/bin/bash
cd /nfs/farm/g/glast/u26/GWFUP/

source set_env/setup_gwfup.sh

echo "Current date and time: $(date)"
echo "Running on $(hostname) machine with pid $$"
echo "About to submit a new GWFUP job for $3 using the sky map available at $1 and NSIDE $2"

set -x
python -u fermi_gw_toolkit/fermi_gw_toolkit/tools/submit_gwfup_job.py --file $1 --nside $2 --version v01 --run_bayul 1 --pixels_job 5 --wall_time 4 --triggername $3

cd -
