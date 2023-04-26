#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

echo 'About to run ATI_plot_map.py for TS... on ADAPTIVEINTERVAL'
python ${FERMI_GWTOOLS}/bin/ATI_plot_map.py --map ${ATI_OUTTSMAP} --out_plot ${ATI_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS

chmod a+w ${ATI_OUTTSMAP_PLOT}
