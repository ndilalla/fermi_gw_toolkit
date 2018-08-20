#!/bin/tcsh

# If we do not need to run the LLE analysis, make this fail
if ($RUN_LLE == 0) then
    echo "RUN_LLE = 0, not running LLE analysis, exiting"
    exit 1
endif

echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
rm -rf ${OUTPUT_FILE_PATH}/LLE/*

echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/AdaptiveTimeIntervals.py --in_map $HEALPIX_PATH_MAP --triggertime $TRIGGERTIME --nside $NSIDE_LLE --ft2 $FT2_PATH --roi $ROI --zenith_cut $ZMAX --theta_cut $THETAMAX --output ${OUTLLEINTERVALS} --plot 1
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/AdaptiveTimeIntervals.py --in_map $HEALPIX_PATH_MAP --triggertime $TRIGGERTIME --nside $NSIDE_LLE --ft2 $FT2_PATH --roi $ROI --zenith_cut $ZMAX --theta_cut $THETAMAX --output ${OUTLLEINTERVALS} --plot 1
mv ${OUTPUT_FILE_PATH}/lle_adaptive_coverage_map.png ${OUTPUT_FILE_PATH}/images/.
chmod -R a+w ${OUTPUT_FILE_PATH}/images/*.png
if ($SIMULATE_MODE == 2) then
exit 1
endif 

