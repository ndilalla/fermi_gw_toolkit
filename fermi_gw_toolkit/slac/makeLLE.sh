#!/bin/bash
echo 'Create a staging directory:'
export stage=${LSCRATCH}
echo $stage
cd $stage
echo PWD=$PWD
export HOME=$PWD
source ${GPL_TASKROOT}/set_env/gtgrb_py39.sh
#export PATH=${GRBSW}/bbbd/scripts:${PATH}

export PFILES=".;$PFILES:$GPL_TASKROOT/pfiles:$HEADAS/syspfiles:$CONDA_PREFIX/share/fermitools/syspfiles"
export PFILES=${PWD}/pfiles:$PFILES
mkdir -pv ${PWD}/pfiles

chmod 777 /sdf/group/fermi/g/grb/GBMTRIGCAT-v2/pfiles/fchecksum.par
chmod 777 /sdf/group/fermi/g/grb/GBMTRIGCAT-v2/pfiles/fmerge.par
chmod 777 /sdf/group/fermi/g/grb/GBMTRIGCAT-v2/pfiles/fcopy.par
chmod 777 /sdf/group/fermi/g/grb/GBMTRIGCAT-v2/pfiles/gtbin.par
chmod 777 /sdf/group/fermi/g/grb/GBMTRIGCAT-v2/pfiles/gtmktime.par
chmod 777 /sdf/group/fermi/g/grb/GBMTRIGCAT-v2/pfiles/gtselect.par

which bbbd_lle.py
which makeLLE.py

set -x

makeLLE.py --ttime $TRIGGERTIME --ra $OBJ_RA --dec $OBJ_DEC --tstart $TSTART --tstop $TSTOP --outdir $stage --version 0 --name $TRIGGERNAME --clobber 1 --regenerate_after_detection 1 --radius -1 --thetamax 89 --zmax 90 --ignore_theta 1

mkdir -p $OUTPUT_FILE_PATH/LLE
ls $stage/$TRIGGERNAME/v00/*
mv $stage/$TRIGGERNAME/v00/$TRIGGERNAME_*_res.txt $OUTPUT_FILE_PATH/LLE/.
mv $stage/$TRIGGERNAME/v00/gll_quick_*.png ${OUTPUT_FILE_PATH}/LLE/gll_quick_${OBJ_RA}_${OBJ_DEC}_${TSTART}_${TSTOP}.png

if ls $stage/$TRIGGERNAME/v00/gll_detec_*.png 1> /dev/null 2>&1; then
    mv $stage/$TRIGGERNAME/v00/gll_detec_*.png ${OUTPUT_FILE_PATH}/LLE/gll_detec_${OBJ_RA}_${OBJ_DEC}_${TSTART}_${TSTOP}.png
fi

echo "Done!" 

#--before BEFORE
#[--after AFTER]
