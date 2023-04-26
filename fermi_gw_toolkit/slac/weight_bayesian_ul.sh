#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXECUTE THE PYTHON SCRIPT

if ($BAYESIAN_UL == 1) then
    echo 'sourcing the setup script!'
    source $GPL_TASKROOT/set_env/setup_gwfup.csh

    set echo

    echo 'About to run weight_bayesian_ul.py..'
    python ${FERMI_GWTOOLS}/bin/weight_bayesian_ul.py --map ${HEALPIX_PATH_MAP} --ul_directory ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/ --outroot ${OUT_BAYUL} --db_file ${GW_DB_FILE_PATH}

    chmod a+w "${OUT_BAYUL}_ph.png"
    chmod a+w "${OUT_BAYUL}_ene.png"
    chmod a+w "${OUT_BAYUL}_diff_ph.png"
    chmod a+w "${OUT_BAYUL}_diff_ene.png"
else
    echo "Bayesian UL not enabled. Skipping this task..."
endif

echo "Done!"
