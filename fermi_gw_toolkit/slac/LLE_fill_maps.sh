#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
echo 'About to run LLE_fill_maps.py..'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE_LLE} --text_file ${OUTPUT_FILE_PATH}/LLE/${TRIGGERNAME}_res_all.txt --out_uls_map ${LLE_OUTULMAP} --out_ts_map ${LLE_OUTTSMAP}
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE_LLE} --text_file ${OUTPUT_FILE_PATH}/LLE/${TRIGGERNAME}_res_all.txt --out_uls_map ${LLE_OUTULMAP} --out_ts_map ${LLE_OUTTSMAP}

chmod a+w ${LLE_OUTULMAP}
chmod a+w ${LLE_OUTTSMAP}
