#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
if ( -e "$LLE_OUTTSMAP" ) then
    echo 'sourcing the setup script!'
    source $GPL_TASKROOT/set_env/setup_gwfup.csh

    set echo

    echo "About to run ATI_plot_map.py for LLE analysis"
    python ${FERMI_GWTOOLS}/bin/ATI_plot_map.py --map ${LLE_OUTTSMAP} --out_plot ${LLE_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type SIG

    chmod a+w ${LLE_OUTTSMAP_PLOT}
endif
