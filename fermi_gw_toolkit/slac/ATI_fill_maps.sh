#!/bin/tcsh -fe
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

echo 'About to run ATI_fill_maps.py..'
python ${FERMI_GWTOOLS}/bin/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${ATI_OUTULMAP} --out_ts_map ${ATI_OUTTSMAP}

chmod a+w ${ATI_OUTULMAP}
chmod a+w ${ATI_OUTTSMAP}
