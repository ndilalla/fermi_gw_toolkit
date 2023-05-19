#!/bin/bash -fe
echo SIMULATE_MODE=$SIMULATE_MODE
echo 'Sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.sh

set -x

#touch $GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt
#chmod a+w $GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt

mkdir -p $DATA_PATH
mkdir -p $OUTPUT_FILE_PATH/images

chmod -R a+w $DATA_PATH
#chmod -R a+w $GPL_TASKROOT/input
#chmod -R a+w $GPL_TASKROOT/output
#chmod -R a+w $OUTPUT_FILE_PATH/images
chmod -R a+w $OUTPUT_FILE_PATH

if [ $SIMULATE_MODE -eq 1 ]; then
    exit 1
fi

echo Checking if $HEALPIX_PATH is working properly
python ${FERMI_GWTOOLS}/bin/check_ligo_map.py $HEALPIX_PATH

echo Coping the $HEALPIX_PATH to $HEALPIX_PATH_MAP
cp $HEALPIX_PATH $HEALPIX_PATH_MAP
if [ -f $FT1_PATH ];
then
    echo 'Removing previously downloaded '$FT1_PATH
    rm $FT1_PATH 
fi
if [ -f $FT2_PATH ];
then
    echo 'Removing previously downloaded '$FT2_PATH
    rm $FT2_PATH 
fi
echo 'Getting the data...'

python ${FERMI_GWTOOLS}/bin/download_LAT_data.py --outdir $DATA_PATH --ft1 $FT1_NAME --ft2 $FT2_NAME --tstart $MET_FT2TSTART --tstop $MET_FT2TSTOP --padding 1000 --one_sec True

if [ ! -f $FT1_PATH ];
then
    exit 1
fi

if [ ! -f $FT2_PATH ];
then
    exit 1
fi

chmod a+w $FT1_PATH
chmod a+w $FT2_PATH
ls -l $DATA_PATH