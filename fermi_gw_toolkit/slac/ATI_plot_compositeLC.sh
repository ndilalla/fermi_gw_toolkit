#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

echo 'About to run plot_lightcurve.py'
python ${FERMI_GWTOOLS}/bin/plot_lightcurve.py --input ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --triggertime $TRIGGERTIME --out_plot ${ATI_COMPOSITELC_PLOT} --nside $NSIDE --xlabel $TRIGGERNAME --histo 1 --type EFLUX

chmod a+w ${ATI_COMPOSITELC_PLOT}
