#!/bin/tcsh -fe
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_mpl.csh
echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/plot_lighcturve.py --input ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --triggertime $TRIGGERTIME --out_plot ${ATI_COMPOSITELC_PLOT} --nside $NSIDE --xlabel $TRIGGERNAME --histo 1 --type EFLUX
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/plot_lighcturve.py --input ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --triggertime $TRIGGERTIME --out_plot ${ATI_COMPOSITELC_PLOT} --nside $NSIDE --xlabel $TRIGGERNAME --histo 1 --type EFLUX
chmod a+w ${ATI_COMPOSITELC_PLOT}
