#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
if ($BAYESIAN_UL == 1) then
    echo 'sourcing the setup script!'
    source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
    echo 'About to run weight_bayesian_ul.py..'
    echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/weight_bayesian_ul.py --map ${HEALPIX_PATH_MAP} --ul_directory ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/ --outroot ${OUT_BAYUL} --db_file ${GPL_TASKROOT}/output/db_gw_events.pkl
    python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/weight_bayesian_ul.py --map ${HEALPIX_PATH_MAP} --ul_directory ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/ --outroot ${OUT_BAYUL} --db_file ${GPL_TASKROOT}/output/db_gw_events.pkl
    chmod a+w "${OUT_BAYUL}_ph.png"
    chmod a+w "${OUT_BAYUL}_ene.png"
    chmod a+w "${OUT_BAYUL}_diff_ph.png"
    chmod a+w "${OUT_BAYUL}_diff_ene.png"
else
    echo "Bayesian UL not enabled. Skipping this task..."
endif

