#!/bin/tcsh

# If we do not need to run the FTI analysis, make this fail
if ($RUN_FTI == 0) then
exit 1
endif

# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
rm -rf ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/*
echo 'About run the prepare_grid.py script...'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/prepare_grid.py --map $HEALPIX_PATH_MAP --out_list $OUTLIST --out_map $OUTMAP --nside $NSIDE --cl $LIGO_COVERAGE_CL
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/prepare_grid.py --map $HEALPIX_PATH_MAP --out_list $OUTLIST --out_map $OUTMAP --nside $NSIDE --cl $LIGO_COVERAGE_CL 
