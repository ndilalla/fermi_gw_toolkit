#!/bin/tcsh -e
# THIS SHOULD SOURCE THE APPROPRIATE FILES TO SET UP THE ENVIRONMENT AND EXCECUTE THE PYTHON SCRIPT
setenv GPL_TASKROOT /nfs/farm/g/glast/u26/GWPIPELINE
setenv TRIGGERNAME bnG299232
setenv TRIGGERTIME 5.25359622983E8

setenv VERSION v01
setenv NSIDE 128

setenv OUTPUT_FILE_PATH ${GPL_TASKROOT}/output/${TRIGGERNAME}/${VERSION}

setenv ATI_COMPOSITELC_PLOT ${OUTPUT_FILE_PATH}/images/ATI_compositeLC_tmp.png
setenv ATI_OUTTSMAP ${OUTPUT_FILE_PATH}/ATI_ts_map_tmp.fits
setenv ATI_OUTTSMAP_PLOT ${OUTPUT_FILE_PATH}/images/ATI_ts_map_tmp.png
setenv ATI_OUTULMAP ${OUTPUT_FILE_PATH}/ATI_ul_map_tmp.fits
setenv ATI_OUTULMAP_PLOT ${OUTPUT_FILE_PATH}/images/ATI_ul_map_tmp.png

setenv FTI_OUTTSMAP ${OUTPUT_FILE_PATH}/FTI_ts_map_tmp.fits
setenv FTI_OUTTSMAP_PLOT ${OUTPUT_FILE_PATH}/images/FTI_ts_map_tmp.png
setenv FTI_OUTULMAP ${OUTPUT_FILE_PATH}/FTI_ul_map_tmp.fits
setenv FTI_OUTULMAP_PLOT ${OUTPUT_FILE_PATH}/images/FTI_ul_map_tmp.png

echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_gw_giacomvst.csh

echo 'About to run FTI_merge_results.py...'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/merge_results.py $TRIGGERNAME --txtdir ${OUTPUT_FILE_PATH}/FIXEDINTERVAL --keyword res
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/merge_results.py $TRIGGERNAME --txtdir ${OUTPUT_FILE_PATH}/FIXEDINTERVAL --keyword res
chmod a+w ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/${TRIGGERNAME}_res_all.txt

echo 'About to run ATI_merge_results.py...'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/merge_results.py $TRIGGERNAME --txtdir ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL --keyword res
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/merge_results.py $TRIGGERNAME --txtdir ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL --keyword res
chmod a+w ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt

echo 'About to run FTI_fill_maps.py..'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${FTI_OUTULMAP} --out_ts_map ${FTI_OUTTSMAP}
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/FIXEDINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${FTI_OUTULMAP} --out_ts_map ${FTI_OUTTSMAP}
chmod a+w ${FTI_OUTULMAP}
chmod a+w ${FTI_OUTTSMAP}

echo 'About to run ATI_fill_maps.py..'
echo python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${ATI_OUTULMAP} --out_ts_map ${ATI_OUTTSMAP}
python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/fill_maps.py --nside ${NSIDE} --text_file ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --out_uls_map ${ATI_OUTULMAP} --out_ts_map ${ATI_OUTTSMAP}
chmod a+w ${ATI_OUTULMAP}
chmod a+w ${ATI_OUTTSMAP}

echo 'sourcing the setup script!'
source $GPL_TASKROOT/config/DEV/setup_mpl.csh
echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${ATI_OUTTSMAP} --out_plot ${ATI_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${ATI_OUTTSMAP} --out_plot ${ATI_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
chmod a+w ${ATI_OUTTSMAP_PLOT}

echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${ATI_OUTULMAP} --out_plot ${ATI_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${ATI_OUTULMAP} --out_plot ${ATI_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX
chmod a+w ${ATI_OUTULMAP_PLOT}

echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${FTI_OUTTSMAP} --out_plot ${FTI_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${FTI_OUTTSMAP} --out_plot ${FTI_OUTTSMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale linear --cmap jet --map_type TS
chmod a+w ${FTI_OUTTSMAP_PLOT}

echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${FTI_OUTULMAP} --out_plot ${FTI_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/ATI_plot_map.py --map ${FTI_OUTULMAP} --out_plot ${FTI_OUTULMAP_PLOT} --min_percentile 0 --max_percentile 100 --zscale log --cmap jet --map_type EFLUX
chmod a+w ${FTI_OUTULMAP_PLOT}

echo  $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/plot_lighcturve.py --input ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --triggertime $TRIGGERTIME --out_plot ${ATI_COMPOSITELC_PLOT} --nside $NSIDE --xlabel $TRIGGERNAME --histo 1 --type EFLUX
$GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/plot_lighcturve.py --input ${OUTPUT_FILE_PATH}/ADAPTIVEINTERVAL/${TRIGGERNAME}_res_all.txt --triggertime $TRIGGERTIME --out_plot ${ATI_COMPOSITELC_PLOT} --nside $NSIDE --xlabel $TRIGGERNAME --histo 1 --type EFLUX
chmod a+w ${ATI_COMPOSITELC_PLOT}

echo 'All Done!'