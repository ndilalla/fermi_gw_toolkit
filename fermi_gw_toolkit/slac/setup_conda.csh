#! /bin/tcsh -f
echo 'Setting up conda!'
#export TMPDIR=$HOME/tmp/pip
# HEADAS Distribution
setenv BASEDIR /nfs/farm/g/glast/u26/GWPIPELINE/
setenv PFILES ''
setenv HOME $BASEDIR
source /afs/slac/g/glast/groups/grb/gw_environment/setup_gw_conda.csh
echo 'source done!'
#setenv HEADAS /afs/slac/g/ki/software/heasoft/6.16/amd64_rhel60/heasoft/x86_64-unknown-linux-gnu-libc2.12
#source ${HEADAS}/headas-init.sh
setenv TMPDIR ''
setenv GRBANALYSIS_DIR ${BASEDIR}/GRBAnalysis_ScienceTools
setenv LLE_DIR ${GRBANALYSIS_DIR}/LLE
#export GBMTOOLS_DIR=${INST_DIR}/GBMtoolkit
#export AUTOFIT_XSPEC_SCRIPT=${INST_DIR}/GtGRB/python/GTGRB

setenv GTGRB_DIR ${GRBANALYSIS_DIR}/GtGRB
setenv MAKELLE_DIR ${GRBANALYSIS_DIR}/makeLLEproducts
setenv GBMTOOLS_DIR ${GRBANALYSIS_DIR}/GBMtoolkit
setenv PFILES ${PWD}/pfiles:$PFILES

# Extra GtGRB setup
#setenv LLE_DIR ${GTGRB_DIR}/LLE

#setenv AUTOFIT_XSPEC_SCRIPT ${GTGRB_DIR}/GtGRB/python/GTGRB

#LLE repository path
setenv LLEREPOSITORY ftp://legacy.gsfc.nasa.gov/fermi/data/lat/triggers
#setenv LLEREPOSITORY /afs/slac/g/glast/groups/grb/LLEProduct-Release

# P7REPOSITORY path
setenv FT2REPOSITORY P8_P305
setenv LLEIFILE $MAKELLE_DIR/python/config_LLE_DRM/Pass8.txt
setenv MCBASEDIR /MC-Tasks/ServiceChallenge/GRBSimulator-Pass8

# HOME MUST POINT TO A WRITABLE DIRECTORY!
#setenv BASEDIR /nfs/farm/g/glast/u26/MC-tasks/makeLLE
#setenv HOME ${BASEDIR}


### Point to or create directory structure
setenv INDIR ${BASEDIR}/DATA/FITS
setenv OUTDIR ${BASEDIR}/DATA/GRBOUT
setenv LOGS ${BASEDIR}/logfiles


setenv PYTHONPATH ${GTGRB_DIR}/python:${GTGRB_DIR}/python/app:${GTGRB_DIR}/python/GTGRB:${GTGRB_DIR}/python/pipeline:${GTGRB_DIR}/python/scripts:${MAKELLE_DIR}/python:${GBMTOOLS_DIR}/python:${PYTHONPATH}
setenv PATH ${GTGRB_DIR}/python/app:${GTGRB_DIR}/python/scripts:${PATH}

#/nfs/slac/g/glast/users/glground/omodei/LOCAL/lib/python2.7/site-packages/:${PYTHONPATH}
#setenv PYTHONPATH ${GTGRB_DIR}/python/app:${PYTHONPATH}
#setenv PATH ${GTGRB_DIR}/python/app:${PATH}
#/nfs/slac/g/glast/users/glground/omodei/LOCAL/bin:/u/gl/omodei/.local/bin/:${PATH}
#setenv PATH ${GTGRB_DIR}/python/pipeline:${PATH}

#setenv BKGE_DATADIR "/afs/slac/g/glast/groups/grb/BKGESTIMATOR_FILES/Bkg_Estimator"
setenv GTGRB_USE_DATACATALOG no
####################################################################
# Diffuse models for pass7 & Pass8
setenv DIFFUSEMODELS_PATH '$CONDA_PREFIX/share/fermitools/refdata/fermi/galdiffuse/'
#/afs/slac/g/glast/groups/grb/diffuseModels/'

# FERMI SOURCE CATALOG
setenv FERMISOURCECATALOG '/afs/slac/g/glast/groups/grb/DATA/CATALOGS/gll_psc_v16.fit'
setenv GTGRB_USE_PRIOR 1
#####################################################################
#setenv CUSTOM_IRF_DIR /afs/slac/g/glast/groups/canda/standard/custom_irfs
#setenv CUSTOM_IRF_NAMES P8_TRANSIENT_SFR_V4,P8_TRANSIENT_ALLTKR_R100_V4,P8_TRANSIENT_TKRONLY_R100_V4,P8_TRANSIENT_TKRONLY_R020_V4,P8_TRANSIENT_TKRONLY_R010_V4,P8_TRANSIENT_R010_V4,P8_TRANSIENT_R020_V4,P8_TRANSIENT_R100_V4,P8_SOURCE_V4,P8_CLEAN_V4,P8_ULTRACLEAN_V4

#####################################################################
setenv MPLBACKEND "Agg"
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
