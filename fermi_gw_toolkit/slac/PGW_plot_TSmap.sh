#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_mpl.csh
echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${PGW_OUTTSMAP} --out_plot ${PGW_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${PGW_OUTTSMAP} --out_plot ${PGW_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
chmod a+w ${PGW_OUTTSMAP_PLOT}