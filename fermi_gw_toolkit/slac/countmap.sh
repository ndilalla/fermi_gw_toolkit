#!/bin/tcsh -f
# If we do not need to run the FTI analysis, make this fail
if ($RUN_PGW == 0) then
exit 1
endif

# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

echo 'running gtselect...'
gtselect infile=${FT1_PATH} outfile=${PGW_FT1} ra=180 dec=0 rad=180 tmin=${MET_TSTART} tmax=${MET_TSTOP} emin=${EMIN} emax=${EMAX} zmax=${ZMAX}

echo 'About to create the counts map'
gtbin evfile=${PGW_FT1} scfile=${FT2_PATH} outfile=${PGW_OUTCMAP}.fits algorithm=CMAP emin=${EMIN} emax=${EMAX} tstart=${MET_TSTART} tstop=${MET_TSTOP} xref=0 yref=0 nxpix=650 nypix=325 binsz=0.5 coordsys=GAL axisrot=0 proj=AIT