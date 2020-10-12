#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_mpl.csh
echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${PGW_OUTULMAP} --out_plot ${PGW_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${PGW_OUTULMAP} --out_plot ${PGW_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX
chmod a+w ${PGW_OUTULMAP_PLOT}