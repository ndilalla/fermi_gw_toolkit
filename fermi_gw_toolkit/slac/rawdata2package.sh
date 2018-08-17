#!/bin/tcsh -e
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT

echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
echo 'About to run the rawdata2package.py script...'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/rawdata2package.py --ft1 $FT1_PATH --ft2 $FT2_PATH --triggername $TRIGGERNAME --triggertime $TRIGGERTIME --outdir $OUTPUT_FILE_PATH/$TRIGGERNAME
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/rawdata2package.py --ft1 $FT1_PATH --ft2 $FT2_PATH --triggername $TRIGGERNAME --triggertime $TRIGGERTIME --outdir $OUTPUT_FILE_PATH/$TRIGGERNAME
chmod -R 777 $OUTPUT_FILE_PATH

