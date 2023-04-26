#!/bin/bash
cd /nfs/farm/g/glast/u26/GWFUP/

source set_env/setup_gwfup.sh

echo "Current date and time: $(date)"
echo "About to submit a new GWFUP job using the sky map at $1"

set -x
python fermi_gw_toolkit/fermi_gw_toolkit/tools/submit_gwfup_job.py --url $1 --nside 64 --version v01 --run_bayul 1 --pixels_job 5 --wall_time 4

cd -
