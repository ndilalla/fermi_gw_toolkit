#!/bin/bash -e
echo SIMULATE_MODE=$SIMULATE_MODE
echo 'Sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_conda.sh

touch $GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt
chmod a+w $GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt

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
# I download the data also before the trigger...
echo getLATFitsFiles.py --output-ft1 $FT1_PATH --output-ft2 $FT2_PATH --minTimestamp $MET_FT2TSTART --maxTimestamp $MET_FT2TSTOP --name $TRIGGERNAME --noextended
getLATFitsFiles.py --output-ft1 $FT1_PATH --output-ft2 $FT2_PATH --minTimestamp $MET_FT2TSTART --maxTimestamp $MET_FT2TSTOP --name $TRIGGERNAME --noextended

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
