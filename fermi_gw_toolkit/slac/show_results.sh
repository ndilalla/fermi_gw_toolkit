#!/bin/tcsh -fe
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/set_env/setup_gwfup.csh

set echo

python ${FERMI_GWTOOLS}/bin/show_results.py --triggername ${TRIGGERNAME} --triggertime ${TRIGGERTIME} --outfile ${OUTPUT_FILE_PATH}/${TRIGGERNAME}_results.html --emin ${EMIN} --emax ${EMAX} --tstart ${TSTART} --tstop ${TSTOP} --thetamax ${THETAMAX} --zmax ${ZMAX} --roi ${ROI} --irf ${IRFS} --galactic_model ${GAL_MODEL} --strategy ${STRATEGY} --ts_cut ${TSMIN} --ligo_map ${HEALPIX_PATH_MAP} --fti_ts_map ${FTI_OUTTSMAP} --ati_ts_map ${ATI_OUTTSMAP} --lle_ts_map ${LLE_OUTTSMAP} --img_folder ${OUTPUT_FILE_PATH}/images/ --template $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/html/results_template.html --db_file ${GW_DB_FILE_PATH}

echo https://s3df.slac.stanford.edu/pun/sys/dashboard/files/fs//sdf/group/fermi/n/u26/GWFUP/output/${TRIGGERNAME}/${VERSION} > ${OUTPUT_FILE_PATH}/msg.txt

cat ${OUTPUT_FILE_PATH}/msg.txt | mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Results for ${TRIGGERNAME} ${VERSION} ready" nicola.omodei@gmail.com

cat ${OUTPUT_FILE_PATH}/msg.txt | mail -r ndilalla@stanford.edu -s "GWFUP Pipeline: Results for ${TRIGGERNAME} ${VERSION} ready" ndilalla@stanford.edu

# this sends the mail to the SLAC fermigw channel:
#mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Results for ${TRIGGERNAME} ${VERSION} ready" o2x6m0g8y0j6y5i7@fermi-lat.slack.com <  ${OUTPUT_FILE_PATH}/msg.txt

#mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Results for ${TRIGGERNAME} ${VERSION} ready" balist@glast2.stanford.edu <  ${OUTPUT_FILE_PATH}/msg.txt

# this triggers the copy to stanford
#chmod a+w $GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt
if ( -f "$GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt" ) then
    mv $GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt $GPL_TASKROOT/status/done/
endif
if ( -f "$GPL_TASKROOT/status/copied/${TRIGGERNAME}_${VERSION}.txt" ) then
    mv $GPL_TASKROOT/status/copied/${TRIGGERNAME}_${VERSION}.txt $GPL_TASKROOT/status/done/
endif

echo 'All done!'
