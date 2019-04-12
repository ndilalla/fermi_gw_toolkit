#! /bin/bash
echo 'Setting up conda!'
#export TMPDIR=$HOME/tmp/pip
# HEADAS Distribution
export BASEDIR=/nfs/farm/g/glast/u26/GWPIPELINE/
export PFILES=''
# HOME MUST POINT TO A WRITABLE DIRECTORY!
export HOME=$BASEDIR
source /afs/slac/g/glast/groups/grb/gw_environment/setup_gw_conda.sh
echo 'source done!'
export TMPDIR=''
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
