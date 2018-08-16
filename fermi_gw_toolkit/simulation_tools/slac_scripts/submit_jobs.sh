#!/usr/bin/env bash

######################################################################################################
# Settings: CHANGE ME                                                                                #
######################################################################################################

# Path to the one_job.sh script
# DO NOT USE the version in the fermi_gw_toolkit package. Instead, copy that file somewhere and modify the
# parameters, then point to the copied version
one_job_path=/afs/slac.stanford.edu/u/gl/giacomov/workspace/gw_sims/one_job.sh

# Path to the directory where to store log files
# Should be an absolute path in the network file system, accessible from the nodes
logpath=/afs/slac.stanford.edu/u/gl/giacomov/workspace/gw_sims/logs

# How many jobs shall we submit? This number times the n_simulations number in the one_job.sh file
# will give the number of ft1 files produced
n_jobs=1000

# Wall time. Jobs lasting more than this number of minutes will be killed, so adjust this number
# according to the n_simulations number in one_job.sh. One simulation takes around 15 min (most of which are spent
# in the gtdiffrsp part), so this number should be larger than 15 x n_simulations
wall_time=80

######################################################################################################
# End of config. Do not change beyond this line                                                      #
######################################################################################################

# Loop and submit the jobs
for ((i=1;i<=n_jobs;i++)); do

    bsub -W ${wall_time} -J GWSIM${i} -C 0 -R "select[rhel60] rusage[mem=8192]" -o ${logpath}/GWSIM${i}.log \
         ${one_job_path}

done
