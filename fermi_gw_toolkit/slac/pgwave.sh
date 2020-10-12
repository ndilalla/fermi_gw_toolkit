#!/bin/tcsh -f
# If we do not need to run the FTI analysis, make this fail
if ($RUN_PGW == 0) then
exit 1
endif

# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh
#rm -rf ${OUTPUT_FILE_PATH}/PGWAVE/*
echo 'run pgwave'
echo pgwave2D input_file=${PGW_OUTCMAP}.fits bgk_choise=n circ_square=s N_scale=1 scala=2.5 otpix=4 n_sigma=7 median_box=3 r_threshold=0.5 kappa=3 min_pix=5 m_num=10 
pgwave2D input_file=${PGW_OUTCMAP}.fits bgk_choise=n circ_square=s N_scale=1 scala=2.5 otpix=4 n_sigma=7 median_box=3 r_threshold=0.5 kappa=3 min_pix=5 m_num=10 
chmod a+r ${PGW_OUTCMAP}.reg
chmod a+r ${PGW_OUTCMAP}.list
