#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

echo 'About to run ATI_plot_map.py for UL... on ADAPTIVEINTERVAL'
CMD="python ${FERMI_GWTOOLS}/bin/ATI_plot_map.py --map ${ATI_OUTULMAP} --out_plot ${ATI_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX"
echo $CMD
$CMD

chmod a+w ${ATI_OUTULMAP_PLOT}
