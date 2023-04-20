#!/bin/tcsh -f
# If we do not need to run the FTI analysis, make this fail
if ($RUN_PGW == 0) then
exit 1
endif

# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
echo 'sourcing the setup script for pgwave!'
source $GPL_TASKROOT/set_env/setup_pgwave.csh

#rm -rf ${OUTPUT_FILE_PATH}/PGWAVE/*
echo 'About to run pgwave'
CMD="pgwave2D input_file=${PGW_OUTCMAP}.fits bgk_choise=n circ_square=s N_scale=1 scala=2.5 otpix=4 n_sigma=7 median_box=3 r_threshold=0.5 kappa=3 min_pix=5 m_num=10"
echo $CMD
$CMD

chmod a+r ${PGW_OUTCMAP}.reg
chmod a+r ${PGW_OUTCMAP}.list
