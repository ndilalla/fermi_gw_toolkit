#!/bin/tcsh -e
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
echo 'About to run FTI_fill_maps.py..'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${FTI_OUTULMAP} --out_ts_map ${FTI_OUTTSMAP}
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${FTI_OUTULMAP} --out_ts_map ${FTI_OUTTSMAP}
chmod a+w ${FTI_OUTULMAP}
chmod a+w ${FTI_OUTTSMAP}
