#!/bin/tcsh -fe
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT

echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_mpl.csh
echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${ATI_OUTTSMAP} --out_plot ${ATI_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${ATI_OUTTSMAP} --out_plot ${ATI_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
chmod a+w ${ATI_OUTTSMAP_PLOT}
