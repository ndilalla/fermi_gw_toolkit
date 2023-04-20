#!/bin/tcsh -fe
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'Create a staging directory:'
setenv stage /scratch/${PIPELINE_TASKPATH}_${LSB_BATCH_JID}
setenv FT2_PATH_STAGE $stage/FT2.fits
setenv TAR_STAGE $stage/TAR.tar
echo $stage 
mkdir -p $stage
#mkdir -p $stage/diffuse
cd $stage
if ( -e $SIMULATE_ROI_TARFILE ) then
    cp $SIMULATE_ROI_TARFILE $TAR_STAGE 
else
    setenv TAR_STAGE None
endif

cp $FT2_PATH $FT2_PATH_STAGE
cp -r $OUTPUT_FILE_PATH/$TRIGGERNAME $stage/.
setenv OUTPUT_FILE_PATH_STAGE $stage

#cp -r $GTBURST_TEMPLATE_PATH/*.txt $stage/diffuse/.
#setenv GTBURST_TEMPLATE_PATH $stage/diffuse

#cp $GALACTIC_DIFFUSE_TEMPLATE $stage/diffuse/.
#setenv $GALACTIC_DIFFUSE_TEMPLATE $stage/diffuse/*fits

echo PWD=$PWD
ls
#ls diffuse
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh
#What is this command this doing?
#mkdir -p $PFILES 

echo 'About run the process_n_points.py script...'
CMD="python ${FERMI_GWTOOLS}/bin/process_n_points.py $TRIGGERNAME --ra $OBJ_RA --dec $OBJ_DEC --roi $ROI --tstarts ${MET_TSTART} --tstops ${MET_TSTOP} --irf $IRFS --galactic_model $GAL_MODEL --particle_model "$PART_MODEL" --tsmin $TSMIN --emin $EMIN --emax $EMAX --zmax $ZMAX --strategy $STRATEGY --thetamax $THETAMAX --datarepository $OUTPUT_FILE_PATH_STAGE --ulphindex $UL_INDEX --ft2 $FT2_PATH_STAGE --src $SRC --burn_in $BURN_IN --n_samples $N_SAMPLES --bayesian_ul $BAYESIAN_UL --sim_ft1_tar $TAR_STAGE --do_tsmap $DO_TSMAP"
echo $CMD
$CMD


mkdir -p $OUTPUT_FILE_PATH/$SUBDIR
set nonomatch x=(${TRIGGERNAME}_*_res.txt)
if ( -e $x[1] ) then
    ls ${TRIGGERNAME}_*_res.txt 
    mv ${TRIGGERNAME}_*_res.txt $OUTPUT_FILE_PATH/$SUBDIR/.
else
    echo "No results file found!"
endif


set nonomatch y=(${TRIGGERNAME}_*_bayesian_ul*.npz)
if ( -e $y[1] ) then
    ls ${TRIGGERNAME}_*_bayesian_ul*.npz
    mv ${TRIGGERNAME}_*_bayesian_ul*.npz $OUTPUT_FILE_PATH/$SUBDIR/.
    ls ${TRIGGERNAME}_*_corner_plot.png
    mv ${TRIGGERNAME}_*_corner_plot.png $OUTPUT_FILE_PATH/$SUBDIR/.
else
    echo "No bayesian ul results file found!"
endif

set nonomatch z=(${TRIGGERNAME}_*_sim*)
if ( -e $z[1] ) then
    ls ${TRIGGERNAME}_*_sim*
    mv ${TRIGGERNAME}_*_sim* $OUTPUT_FILE_PATH/$SUBDIR/.
else
    echo "No simulation file found!"
endif

set nonomatch k=(${TRIGGERNAME}_*_cmap*)
if ( -e $k[1] ) then
    ls ${TRIGGERNAME}_*_cmap*
    mv ${TRIGGERNAME}_*_cmap* $OUTPUT_FILE_PATH/$SUBDIR/.
    ls ${TRIGGERNAME}_*_tsmap*
    mv ${TRIGGERNAME}_*_tsmap* $OUTPUT_FILE_PATH/$SUBDIR/.
    ls ${TRIGGERNAME}_*_coords.txt 
    mv ${TRIGGERNAME}_*_coords.txt $OUTPUT_FILE_PATH/$SUBDIR/.
else
    echo "No TSMAP and CMAP found!"
endif

echo "Removing staging directory"
rm -rf $stage
echo "Done!"
