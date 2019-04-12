#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'Create a staging directory:'
setenv stage /scratch/${PIPELINE_TASKPATH}_${LSB_BATCH_JID}
echo $stage 
mkdir -p $stage
cd $stage
echo PWD=$PWD
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
mkdir -p $PFILES

echo 'About run the process_n_points_times.py script...'
echo python ${GPL_TASKROOT}/fermi_gw_toolkit/fermi_gw_toolkit/process_n_points_times.py $TRIGGERNAME --ra $OBJ_RA --dec $OBJ_DEC --roi $ROI --tstarts $TSTARTS --tstops $TSTOPS --irf $IRFS --galactic_model $GAL_MODEL --particle_model "$PART_MODEL" --tsmin $TSMIN --emin $EMIN --emax $EMAX --zmax $ZMAX --strategy $STRATEGY --thetamax $THETAMAX --datarepository $OUTPUT_FILE_PATH --ulphindex $UL_INDEX
python ${GPL_TASKROOT}/fermi_gw_toolkit/fermi_gw_toolkit/process_n_points_times.py $TRIGGERNAME --ra $OBJ_RA --dec $OBJ_DEC --roi $ROI --tstarts $TSTARTS --tstops $TSTOPS --irf $IRFS --galactic_model $GAL_MODEL --particle_model "$PART_MODEL" --tsmin $TSMIN --emin $EMIN --emax $EMAX --zmax $ZMAX --strategy $STRATEGY --thetamax $THETAMAX --datarepository $OUTPUT_FILE_PATH --ulphindex $UL_INDEX

mkdir -p $OUTPUT_FILE_PATH/ADAPTIVEINTERVAL
set nonomatch x=(${TRIGGERNAME}_*_res.txt)
if ( -e $x[1] ) then
    ls ${TRIGGERNAME}_*_res.txt 
    mv ${TRIGGERNAME}_*_res.txt $OUTPUT_FILE_PATH/ADAPTIVEINTERVAL/.
else
    echo "No results file found!"
endif
echo 'Removing staging directory:'
rm -rf $stage
