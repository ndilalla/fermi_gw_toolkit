#!/usr/bin/env bash

# Echo all commands so that it is easier to interpret the log
set -x

######################################################################################################
# Settings: CHANGE ME                                                                                #
######################################################################################################

# Path to fermi_gw_toolkit, without the "fermi_gw_toolkit" parts. So
# if the package is at /afs/slac.stanford.edu/u/gl/giacomov/workspace/fermi_gw_toolkit
# then this should be /afs/slac.stanford.edu/u/gl/giacomov/workspace/
export GPL_TASKROOT=/afs/slac.stanford.edu/u/gl/giacomov/workspace/

# Data package absolute path (real data)
# in the network file system accessible from the node
package_path=/afs/slac.stanford.edu/u/gl/giacomov/workspace/gw_sims/original_package/bnGRB

# Directory where to put the simulated FT1 files
# (absolute path in the network file system accessible from the node)
outdir_path=/afs/slac.stanford.edu/u/gl/giacomov/workspace/gw_sims/outdir

# Make sure the PFILES are set correctly, with '.' as first
# thing and then the read-only paths, otherwise you might
# get race conditions
export PFILES=".;${HEADAS}/syspfiles:${INST_DIR}/syspfiles"

# How many simulations per job?
n_simulations=4

# Time interval duration (must be
# shorter or equal to what contained in
# the package)
duration=10000.0

######################################################################################################
# End of config. Do not change beyond this line                                                      #
######################################################################################################


# Make sure the output directory exists, if not create it
mkdir -p $outdir_path

# This is only for testing. If you run on the master (instead of the nodes)
if [ -z ${LSB_JOBID+x} ]; then

    # This is a test run

    echo "IS THIS A TEST? LSB_JOBID is not set!"
    export LSB_JOBID=123456
    export LSB_JOBNAME=FakeJob

    workdir=/dev/shm/`whoami`${LSB_JOBID}

else
    # We are on the node

    workdir=/scratch/`whoami`${LSB_JOBID}

fi

# Create the workdir (if it already exists this will *not* fail)
mkdir -p $workdir

# Move there
cd ${workdir}

for ((i=1;i<=n_simulations;i++)); do

    mkdir -p sim_outdir/bnGRB

    # Make simulation

    python ${GPL_TASKROOT}/fermi_gw_toolkit/fermi_gw_toolkit/automatic_pipeline/simulate_data_package.py \
           --package_path ${package_path} --duration ${duration} --outdir sim_outdir/bnGRB \
           --seed ${LSB_JOBID}00${i}

    # Move the simulated ft1 to the output directory

    mv sim_outdir/bnGRB/gll_ft1* ${outdir_path}/gll_ft1_tr_bnGRB${LSB_JOBNAME}${LSB_JOBID}_v${i}.fit

    rm -rf sim_outdir/bnGRB

done

cd
rm -rf ${workdir}