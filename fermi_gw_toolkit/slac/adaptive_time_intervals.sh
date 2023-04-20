#!/bin/tcsh -f

if ($RUN_ATI == 0) then
    echo "RUN_ATI = 0, not running ATI analysis, exiting"
    exit 2
endif

echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

rm -rf ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/*
echo 'About to run AdaptiveTimeIntervals.py for ATI analysis..'
CMD="python ${FERMI_GWTOOLS}/bin/AdaptiveTimeIntervals.py --in_map $HEALPIX_PATH_MAP --triggertime $TRIGGERTIME --nside $NSIDE --ft2 $FT2_PATH --roi $ROI --zenith_cut $ZMAX --theta_cut $THETAMAX --output ${OUTADAPTIVEINTERVALS} --plot 1"
echo $CMD
$CMD

mv ${OUTPUT_FILE_PATH}/adaptive_coverage_map.png ${OUTPUT_FILE_PATH}/images/.
chmod -R a+w ${OUTPUT_FILE_PATH}/images/*.png

if ($SIMULATE_MODE == 2) then
exit 1
endif
