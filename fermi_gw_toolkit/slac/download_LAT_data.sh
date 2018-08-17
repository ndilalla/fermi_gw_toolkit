#!/bin/bash 
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo TRIGGERNAME=$TRIGGERNAME
TRIGGERNAME=$TRIGGERNAME
emin=$EMIN
emax=$EMAX
outdir=$DATA_PATH
irf=$IRFS
tstart=$TSTART
tstop=$TSTOP
ligo_map=$LIGO_MAP

trigger_time = $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/date_to_met.py 

$TRIGGERTIME=trigger_time

_FT1,_FT2 = $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/download_LAT_data.py

$FT1=_FT1
$FT2=_FT2
