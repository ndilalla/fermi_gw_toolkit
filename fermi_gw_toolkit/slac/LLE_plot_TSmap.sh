#!/bin/tcsh -fe
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_mpl.csh
echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${LLE_OUTTSMAP} --out_plot ${LLE_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type SIG
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${LLE_OUTTSMAP} --out_plot ${LLE_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type SIG
chmod a+w ${LLE_OUTTSMAP_PLOT}
