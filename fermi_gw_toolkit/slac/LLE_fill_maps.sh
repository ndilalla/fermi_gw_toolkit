#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

echo 'About to run LLE_fill_maps.py..'
python ${FERMI_GWTOOLS}/bin/fill_maps.py --nside ${NSIDE_LLE} --text_file ${OUTPUT_FILE_PATH}/LLE/${TRIGGERNAME}_res_all.txt --out_uls_map ${LLE_OUTULMAP} --out_ts_map ${LLE_OUTTSMAP}

if ( -e "$LLE_OUTULMAP" ) then
    chmod a+w ${LLE_OUTULMAP}
endif
if ( -e "$LLE_OUTTSMAP" ) then
    chmod a+w ${LLE_OUTTSMAP}
endif
