#! /bin/bash
echo 'Setting up conda!'

unset LD_LIBRARY_PATH
unset PYTHONPATH

export BASEDIR=/nfs/farm/g/glast/u26/GWPIPELINE/

export PFILES=''
# HOME MUST POINT TO A WRITABLE DIRECTORY!
export HOME=$BASEDIR

#source $BASEDIR/setup_gw_conda.sh

export GWENV=/nfs/farm/g/glast/g/grb/gw_environment
export PATH=${GWENV}/miniconda3/bin:/usr/lib64/qt-3.3/bin:/opt/lsf-openmpi/1.8.1/bin/:/usr/local/bin:/bin:/usr/bin:/usr/X11R6/bin

# Add gtburst executables to the path
GTBURST_PATH=${GWENV}/miniconda3/envs/fermi_st/lib/python2.7/site-packages/fermitools/GtBurst
export PATH=${PATH}:${GTBURST_PATH}/scripts:${GTBURST_PATH}/commands

export HEADAS=/afs/slac/g/ki/software/heasoft/6.24/amd64_rhel60/heasoft/x86_64-pc-linux-gnu-libc2.12
source $HEADAS/headas-init.sh

source activate fermi_st

export PFILES=".;/afs/slac/g/ki/software/heasoft/6.24/amd64_rhel60/heasoft/x86_64-pc-linux-gnu-libc2.12/syspfiles:${GWENV}/miniconda3/envs/fermi_st/share/fermitools/syspfiles"
#export PYTHONPATH=${GTBURST_PATH}/scripts:${PYTHONPATHH}/commands
export PYTHONPATH=${GTBURST_PATH}/scripts:${BASEDIR}/fermi_gw_toolkit

unset GTBURST_TEMPLATE_PATH
unset GALACTIC_DIFFUSE_TEMPLATE

export TMPDIR='/tmp/'
export GRBANALYSIS_DIR=${BASEDIR}/GRBAnalysis_ScienceTools
export LLE_DIR=${GRBANALYSIS_DIR}/LLE
export GTGRB_DIR=${GRBANALYSIS_DIR}/GtGRB
export MAKELLE_DIR=${GRBANALYSIS_DIR}/makeLLEproducts
export GBMTOOLS_DIR=${GRBANALYSIS_DIR}/GBMtoolkit
export PFILES=${PWD}/pfiles:$PFILES
#LLE repository path
export LLEREPOSITORY=ftp://legacy.gsfc.nasa.gov/fermi/data/lat/triggers
#export LLEREPOSITORY /afs/slac/g/glast/groups/grb/LLEProduct-Release

# P7REPOSITORY path
export FT2REPOSITORY=P8_P305
export LLEIFILE=$MAKELLE_DIR/python/config_LLE_DRM/Pass8.txt
export MCBASEDIR=/MC-Tasks/ServiceChallenge/GRBSimulator-Pass8
### Point to or create directory structure
export INDIR=${BASEDIR}/DATA/FITS
export OUTDIR=${BASEDIR}/DATA/GRBOUT
export LOGS=${BASEDIR}/logfiles


export PYTHONPATH=${GTGRB_DIR}/python:${GTGRB_DIR}/python/app:${GTGRB_DIR}/python/GTGRB:${GTGRB_DIR}/python/pipeline:${GTGRB_DIR}/python/scripts:${MAKELLE_DIR}/python:${GBMTOOLS_DIR}/python:${PYTHONPATH}
export PATH=${GTGRB_DIR}/python/app:${GTGRB_DIR}/python/scripts:${PATH}
export GTGRB_USE_DATACATALOG=yes
####################################################################
# Diffuse models for pass7 & Pass8
export DIFFUSEMODELS_PATH='$CONDA_PREFIX/share/fermitools/refdata/fermi/galdiffuse/'
#/afs/slac/g/glast/groups/grb/diffuseModels/'

# FERMI SOURCE CATALOG
export FERMISOURCECATALOG='/afs/slac/g/glast/groups/grb/DATA/CATALOGS/gll_psc_v16.fit'
export GTGRB_USE_PRIOR=1
export MPLBACKEND="Agg"

#####################################################################
#export CUSTOM_IRF_DIR /afs/slac/g/glast/groups/canda/standard/custom_irfs
#export CUSTOM_IRF_NAMES P8_TRANSIENT_SFR_V4,P8_TRANSIENT_ALLTKR_R100_V4,P8_TRANSIENT_TKRONLY_R100_V4,P8_TRANSIENT_TKRONLY_R020_V4,P8_TRANSIENT_TKRONLY_R010_V4,P8_TRANSIENT_R010_V4,P8_TRANSIENT_R020_V4,P8_TRANSIENT_R100_V4,P8_SOURCE_V4,P8_CLEAN_V4,P8_ULTRACLEAN_V4
#####################################################################
echo '...........................................................................'
echo '..........CONFIGURATION FOR GRBANALYSIS........'
echo '...GTGRB_DI.............................:' $GTGRB_DIR
echo '...BASEDIR..............................:' $BASEDIR
echo '...PFILES...............................:' $PFILES
echo '...DIFFUSEMODELS_PATH...................:' $DIFFUSEMODELS_PATH
echo '...FERMISOURCECATALOG...................:' $FERMISOURCECATALOG
echo '...GTGRB_USE_PRIOR......................:' $GTGRB_USE_PRIOR
#echo '...BKGE_DATADIR.........................:' $BKGE_DATADIR
echo '...HEADAS...............................:' $HEADAS
#echo '...ROOTSYS..............................:' $ROOTSYS
echo '...........................................................................'

mkdir -pv ${PWD}/pfiles
mkdir -pv $OUTDIR
mkdir -pv $INDIR
mkdir -pv $INDIR/LAT
mkdir -pv $INDIR/GBM
mkdir -pv $LOGS
