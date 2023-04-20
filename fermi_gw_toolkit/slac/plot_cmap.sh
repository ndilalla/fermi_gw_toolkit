#!/bin/tcsh -f
# If we do not need to run the FTI analysis, make this fail
if ($RUN_PGW == 0) then
exit 1
endif

# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

#rm -rf ${OUTPUT_FILE_PATH}/PGWAVE/*
echo 'About to run plot_cmap'
CMD="python ${FERMI_GWTOOLS}/bin/plot_cmap.py --map ${PGW_OUTCMAP}.fits --out ${PGW_OUTCMAP_PLOT} --pgwlist ${PGW_OUTCMAP}.list --smooth 4 --hpmap $HEALPIX_PATH_MAP --pgwoutlist $PGW_OUTLIST"
echo $CMD
$CMD

chmod a+r ${PGW_OUTCMAP_PLOT}
chmod a+r ${PGW_OUTLIST}
