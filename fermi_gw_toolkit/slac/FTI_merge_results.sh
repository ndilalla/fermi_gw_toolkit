#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

echo 'About to run merge_results.py... on FIXEDINTERVAL'
CMD="python ${FERMI_GWTOOLS}/bin/merge_results.py $TRIGGERNAME --txtdir ${OUTPUT_FILE_PATH}/FIXEDINTERVAL --keyword res"
echo $CMD
$CMD

chmod -R a+w ${OUTPUT_FILE_PATH}/FIXEDINTERVAL
