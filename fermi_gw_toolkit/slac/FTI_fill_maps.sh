#!/bin/tcsh -fe
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

echo 'About to run FTI_fill_maps.py..'
python ${FERMI_GWTOOLS}/bin/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${FTI_OUTULMAP} --out_ts_map ${FTI_OUTTSMAP}

chmod a+w ${FTI_OUTULMAP}
chmod a+w ${FTI_OUTTSMAP}
