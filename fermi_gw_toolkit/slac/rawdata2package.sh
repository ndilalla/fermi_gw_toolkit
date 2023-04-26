#!/bin/bash -ve
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT

echo 'Sourcing the setup script-->'
source $GPL_TASKROOT/set_env/setup_gwfup.sh
echo 'About to run the rawdata2package.py script...'

mkdir -p $OUTPUT_FILE_PATH/$TRIGGERNAME

echo "Creating and moving to $OUTPUT_FILE_PATH/$TRIGGERNAME"
cd $OUTPUT_FILE_PATH/$TRIGGERNAME

python $GTBURST_PATH/scripts/rawdata2package.py $FT1_PATH $FT2_PATH $TRIGGERTIME $TRIGGERNAME 0.0 0.0

chmod -R 777 $OUTPUT_FILE_PATH
#exit(1)
