#!/bin/tcsh -f
echo SIMULATE_MODE=$SIMULATE_MODE
echo 'Sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_conda.csh
#setup_gw_giacomvst.csh
mkdir -p $DATA_PATH
mkdir -p $OUTPUT_FILE_PATH/images

chmod -R a+w $DATA_PATH
#chmod -R a+w $GPL_TASKROOT/input
#chmod -R a+w $GPL_TASKROOT/output
#chmod -R a+w $OUTPUT_FILE_PATH/images
chmod -R a+w $OUTPUT_FILE_PATH

if ($SIMULATE_MODE == 1) then
exit 1
endif
echo Coping the $HEALPIX_PATH to $HEALPIX_PATH_MAP
cp $HEALPIX_PATH $HEALPIX_PATH_MAP
echo 'Removing previously downloaded files...'
rm $FT1_PATH 
rm $FT2_PATH 
echo 'Getting the data...'
# I download the data also nbefore the trigger...
echo getLATFitsFiles.py --output-ft1 $FT1_PATH --output-ft2 $FT2_PATH --minTimestamp $MET_FT2TSTART --maxTimestamp $MET_FT2TSTOP --name $TRIGGERNAME
getLATFitsFiles.py --output-ft1 $FT1_PATH --output-ft2 $FT2_PATH --minTimestamp $MET_FT2TSTART --maxTimestamp $MET_FT2TSTOP --name $TRIGGERNAME

ls $DATA_PATH
