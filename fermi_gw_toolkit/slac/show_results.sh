#!/bin/tcsh -f
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_mpl.csh
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/show_results.py --triggername ${TRIGGERNAME} --triggertime ${TRIGGERTIME} --outfile ${OUTPUT_FILE_PATH}/${TRIGGERNAME}_results.html --emin ${EMIN} --emax ${EMAX} --tstart ${TSTART} --tstop ${TSTOP} --thetamax ${THETAMAX} --zmax ${ZMAX} --roi ${ROI} --irf ${IRFS} --galactic_model ${GAL_MODEL} --strategy ${STRATEGY} --ts_cut ${TSMIN} --ligo_map ${HEALPIX_PATH_MAP} --fti_ts_map ${FTI_OUTTSMAP} --ati_ts_map ${ATI_OUTTSMAP} --lle_ts_map ${LLE_OUTTSMAP} --img_folder ${OUTPUT_FILE_PATH}/images/ --template $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/results_template_pgw.html --db_file ${GPL_TASKROOT}/output/db_gw_events.pkl
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/show_results.py --triggername ${TRIGGERNAME} --triggertime ${TRIGGERTIME} --outfile ${OUTPUT_FILE_PATH}/${TRIGGERNAME}_results.html --emin ${EMIN} --emax ${EMAX} --tstart ${TSTART} --tstop ${TSTOP} --thetamax ${THETAMAX} --zmax ${ZMAX} --roi ${ROI} --irf ${IRFS} --galactic_model ${GAL_MODEL} --strategy ${STRATEGY} --ts_cut ${TSMIN} --ligo_map ${HEALPIX_PATH_MAP} --fti_ts_map ${FTI_OUTTSMAP} --ati_ts_map ${ATI_OUTTSMAP} --lle_ts_map ${LLE_OUTTSMAP} --img_folder ${OUTPUT_FILE_PATH}/images/ --template $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/results_template_pgw.html --db_file ${GPL_TASKROOT}/output/db_gw_events.pkl

echo http://glast-ground.slac.stanford.edu/Decorator/exp/Fermi/Decorate/users/omodei/myHome/GWPIPELINE/output/${TRIGGERNAME}/${VERSION}/${TRIGGERNAME}_results.html > ${OUTPUT_FILE_PATH}/msg.txt

mail -s "Results ${TRIGGERNAME} ${VERSION} ready" nicola.omodei@gmail.com <  ${OUTPUT_FILE_PATH}/msg.txt
mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Results for ${TRIGGERNAME} ${VERSION} ready" nicola.omodei@gmail.com <  ${OUTPUT_FILE_PATH}/msg.txt

mail -r ndilalla@stanford.edu -s "GWFUP Pipeline: Results for ${TRIGGERNAME} ${VERSION} ready" ndilalla@stanford.edu <  ${OUTPUT_FILE_PATH}/msg.txt

# this send the mail to the SLAC fermigw channel:
#mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Results for ${TRIGGERNAME} ${VERSION} ready" o2x6m0g8y0j6y5i7@fermi-lat.slack.com <  ${OUTPUT_FILE_PATH}/msg.txt

#mail -r nicola.omodei@gmail.com -s "GWFUP Pieline: Results for ${TRIGGERNAME} ${VERSION} ready" balist@glast2.stanford.edu <  ${OUTPUT_FILE_PATH}/msg.txt

# this triggers the copy to stanford
rm $GPL_TASKROOT/status/running/${TRIGGERNAME}_${VERSION}.txt
touch $GPL_TASKROOT/status/done/${TRIGGERNAME}_${VERSION}.txt
chmod a+w $GPL_TASKROOT/status/done/${TRIGGERNAME}_${VERSION}.txt
