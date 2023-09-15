#!/bin/tcsh -e
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'Create a staging directory:'
setenv stage ${LSCRATCH}
echo $stage
cd $stage
echo PWD=$PWD
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
mkdir -p $PFILES

echo 'About run the doTimeResolvedLike.py script...'
doTimeResolvedLike.py $TRIGGERNAME --ra $OBJ_RA --dec $OBJ_DEC --roi $ROI --tstarts ${MET_TSTART} --tstops ${MET_TSTOP} --irf $IRFS --galactic_model $GAL_MODEL --particle_model "$PART_MODEL" --tsmin $TSMIN --emin $EMIN --emax $EMAX --zmax $ZMAX --strategy $STRATEGY --datarepository $OUTPUT_FILE_PATH --ulphindex $UL_INDEX --outfile $OUT_FILE

mkdir -p $OUTPUT_FILE_PATH/ADAPTIVEINTERVAL
if ( -f $OUT_FILE ) then
    echo Results=$OUT_FILE
    ls $OUT_FILE
    mv $OUT_FILE $OUTPUT_FILE_PATH/ADAPTIVEINTERVAL/
endif

echo 'Done!'