#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

echo 'About to run get_coverage.py..'
python ${FERMI_GWTOOLS}/bin/get_coverage.py --in_map $HEALPIX_PATH_MAP --ft2 $OUTPUT_FILE_PATH/$TRIGGERNAME/gll_ft2_tr_${TRIGGERNAME}_v00.fit --start_time ${MET_TSTART} --stop_time ${MET_TSTOP} --theta_cut $THETAMAX --zenith_cut $ZMAX --outroot $OUTCOV

mv ${OUTCOV}_coverage.png ${OUTPUT_FILE_PATH}/images/.
mv ${OUTCOV}_prob_coverage.png ${OUTPUT_FILE_PATH}/images/.
chmod -R a+w ${OUTPUT_FILE_PATH}/images/*.png
if ($SIMULATE_MODE == 2) then
    exit 1
endif
