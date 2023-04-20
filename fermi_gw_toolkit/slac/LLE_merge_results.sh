#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

mkdir -p ${OUTPUT_FILE_PATH}/LLE
echo 'About to run LLE_merge_results.py...'
CMD="python ${FERMI_GWTOOLS}/bin/merge_results.py $TRIGGERNAME --txtdir ${OUTPUT_FILE_PATH}/LLE --keyword res"
echo $CMD
$CMD

chmod -R a+w ${OUTPUT_FILE_PATH}/LLE
