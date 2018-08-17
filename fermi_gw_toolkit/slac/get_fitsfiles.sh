#!/bin/tcsh 
echo SIMULATE_MODE=$SIMULATE_MODE
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
mkdir -p $DATA_PATH
mkdir -p $OUTPUT_FILE_PATH/images

#chmod -R 777 $DATA_PATH
chmod -R a+w $GPL_TASKROOT/input
chmod -R a+w $GPL_TASKROOT/output
chmod -R a+w $OUTPUT_FILE_PATH/images

if ($SIMULATE_MODE == 1) then
exit 1
endif
echo Coping the $HEALPIX_PATH to $HEALPIX_PATH_MAP
cp $HEALPIX_PATH $HEALPIX_PATH_MAP
echo 'Getting the data...'
echo ~glast/astroserver/prod/astro --event-sample P8_P302_BASE --output-ft1 $FT1_PATH --minTimestamp $MET_TSTART --maxTimestamp $MET_TSTOP store --event-class-name Source
~glast/astroserver/prod/astro --event-sample P8_P302_BASE --output-ft1 $FT1_PATH --minTimestamp $MET_TSTART --maxTimestamp $MET_TSTOP store --event-class-name Source

echo ~glast/astroserver/prod/astro --event-sample P8_P302_BASE --output-ft2-1s $FT2_PATH --minTimestamp $MET_FT2TSTART --maxTimestamp $MET_FT2TSTOP storeft2
~glast/astroserver/prod/astro --event-sample P8_P302_BASE --output-ft2-1s $FT2_PATH --minTimestamp $MET_FT2TSTART --maxTimestamp $MET_FT2TSTOP storeft2
ls $DATA_PATH
