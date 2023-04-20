#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

echo 'About to run ATI_plot_map.py for UL... on FIXEDINTERVAL'
CMD="python ${FERMI_GWTOOLS}/bin/ATI_plot_map.py --map ${FTI_OUTULMAP} --out_plot ${FTI_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX"
echo $CMD
$CMD

chmod a+w ${FTI_OUTULMAP_PLOT}
