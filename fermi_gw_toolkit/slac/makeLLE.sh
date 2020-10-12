#!/bin/bash
echo 'Create a staging directory:'
export stage=/scratch/${PIPELINE_TASKPATH}_${LSB_BATCH_JID}  
echo $stage
mkdir -p $stage
cd $stage
echo PWD=$PWD
export HOME=$PWD
source ${GPL_TASKROOT}/setup_gtgrb.sh
which bbbd_lle.py
which makeLLE.py
echo makeLLE.py --ttime $TRIGGERTIME --ra $OBJ_RA --dec $OBJ_DEC --tstart $TSTART --tstop $TSTOP --outdir $stage --version 0 --name $TRIGGERNAME --clobber 1 --regenerate_after_detection 1 --radius -1 --thetamax 89 --zmax 90 --ignore_theta 1 

makeLLE.py --ttime $TRIGGERTIME --ra $OBJ_RA --dec $OBJ_DEC --tstart $TSTART --tstop $TSTOP --outdir $stage --version 0 --name $TRIGGERNAME --clobber 1 --regenerate_after_detection 1 --radius -1 --thetamax 89 --zmax 90 --ignore_theta 1 

mkdir -p $OUTPUT_FILE_PATH/LLE
ls $stage/$TRIGGERNAME/v00/*
mv $stage/$TRIGGERNAME/v00/$TRIGGERNAME_*_res.txt $OUTPUT_FILE_PATH/LLE/.
mv $stage/$TRIGGERNAME/v00/gll_quick_*.png ${OUTPUT_FILE_PATH}/LLE/gll_quick_${OBJ_RA}_${OBJ_DEC}_${TSTART}_${TSTOP}.png


if ls $stage/$TRIGGERNAME/v00/gll_detec_*.png 1> /dev/null 2>&1; then
    mv $stage/$TRIGGERNAME/v00/gll_detec_*.png ${OUTPUT_FILE_PATH}/LLE/gll_detec_${OBJ_RA}_${OBJ_DEC}_${TSTART}_${TSTOP}.png
fi

echo "Removing staging directory"
rm -rf $stage
echo "Done!" 

#--before BEFORE
#[--after AFTER]
