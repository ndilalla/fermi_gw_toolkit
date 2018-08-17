#! /bin/tcsh

set rhversion=`cat /etc/redhat-release | tr -d "a-zA-Z() " | cut -f1 -d"."`

set arch=`uname -a | cut -f12 -d" "`
if ( $rhversion == '5' ) then
    if ( $arch == 'x86_64' ) then
      setenv OS_ARCH redhat5-x86_64-64bit-gcc41
    else
      setenv OS_ARCH redhat5-i686-32bit-gcc41
    endif
endif
if ( $rhversion == '6' ) then
    setenv OS_ARCH redhat6-x86_64-64bit-gcc44
endif

setenv HOME ${PWD}

# HEADAS Distribution
setenv HEADAS /afs/slac/g/ki/software/heasoft/6.16/amd64_rhel60/heasoft/x86_64-unknown-linux-gnu-libc2.12
source ${HEADAS}/headas-init.csh

# SCIENCE TOOLS:
#setenv SCIENCETOOLS_INST ScienceTools-10-01-01
#setenv SCIENCETOOLS_VERSION 10-01-01
setenv SCIENCETOOLS_VERSION 11-05-02
#setenv FERMI_GW_DATA /nfs/farm/g/glast/g/solar/flares/beta-version/pesce/fermi_gw_toolkit/fermi_gw_toolkit/examples/DATA
#setenv FERMI_GW_OUTPUT /nfs/farm/g/glast/g/solar/flares/beta-version/pesce/fermi_gw_toolkit/fermi_gw_toolkit/

setenv BLDTYPE ${OS_ARCH}-Optimized
setenv GLAST_EXT /afs/slac/g/glast/ground/GLAST_EXT/${OS_ARCH}
#setenv ST_DIR /nfs/farm/g/glast/u/giacomov/${SCIENCETOOLS_INST}
setenv ST_DIR /nfs/farm/g/glast/u35/ReleaseManagerBuild/${OS_ARCH}/Optimized/ScienceTools/${SCIENCETOOLS_VERSION}
setenv INST_DIR ${ST_DIR}
setenv FERMI_DIR ${ST_DIR}
setenv GTBURST_DIR /nfs/farm/g/glast/u26/GWPIPELINE/gtburst

setenv BASEDIR ${PWD}
setenv PFILES ${BASEDIR}/pfiles
source $INST_DIR/bin/$BLDTYPE/_setup.csh
echo $INST_DIR/bin/$BLDTYPE/_setup.csh
ls $INST_DIR/bin/$BLDTYPE/_setup.csh
# Extra GtGRB setup
#setenv LLE_DIR ${INST_DIR}/LLE
#setenv GBMTOOLS_DIR ${INST_DIR}/GBMtoolkit
#setenv AUTOFIT_XSPEC_SCRIPT ${INST_DIR}/GtGRB/python/GTGRB

#LLE repository path
#setenv LLEREPOSITORY ftp://legacy.gsfc.nasa.gov/fermi/data/lat/triggers
#setenv LLEREPOSITORY /afs/slac/g/glast/groups/grb/LLEProduct-Release

setenv PYTHONPATH ${GTBURST_DIR}/python:${PYTHONPATH}
setenv PYTHONPATH /nfs/farm/g/glast/u26/GWPIPELINE/fermi_gw_toolkit/:${PYTHONPATH}
setenv PYTHONPATH ${INST_DIR}/python/app:${PYTHONPATH}

#setenv PYTHONPATH /afs/slac/g/glast/groups/solar/flares/beta-version/pesce/fermi_gw_toolkit/:${PYTHONPATH}

#setenv PATH ${INST_DIR}/python/app:${PATH}
#setenv PATH ${INST_DIR}/python/pipeline:${PATH}
setenv PATH ${GTBURST_DIR}/python/GtBurst/commands:${PATH}
setenv PATH ${GTBURST_DIR}/python/GtBurst/scripts:${PATH}

# P7REPOSITORY path
#setenv P7REPOSITORY P7_P202

### Point to or create directory structure
#setenv INDIR ${BASEDIR}/DATA/FITS
#setenv OUTDIR ${BASEDIR}/DATA/GRBOUT
#setenv LOGS ${BASEDIR}/logfiles


#setenv GTGRB_DIR $INST_DIR
#setenv BKGE_DATADIR "/afs/slac/g/glast/groups/grb/BKGESTIMATOR_FILES/Bkg_Estimator"
#setenv GTGRB_USE_DATACATALOG no
#####################################################################
####################################################################
# Diffuse models for pass7 & Pass8
#setenv DIFFUSEMODELS_PATH '/afs/slac/g/glast/groups/grb/diffuseModels/'
# FERMI SOURCE CATALOG

#setenv FERMISOURCECATALOG '/afs/slac/g/glast/groups/grb/DATA/CATALOGS/gll_psc_v08.fit'
#setenv GTGRB_USE_PRIOR 1
#####################################################################

#setenv CUSTOM_IRF_DIR /afs/slac/g/glast/groups/canda/standard/custom_irfs
#setenv CUSTOM_IRF_NAMES P8_TRANSIENT_SFR_V4,P8_TRANSIENT_ALLTKR_R100_V4,P8_TRANSIENT_TKRONLY_R100_V4,P8_TRANSIENT_TKRONLY_R020_V4,P8_TRANSIENT_TKRONLY_R010_V4,P8_TRANSIENT_R010_V4,P8_TRANSIENT_R020_V4,P8_TRANSIENT_R100_V4,P8_SOURCE_V4,P8_CLEAN_V4,P8_ULTRACLEAN_V4

setenv GTBURST_TEMPLATE_PATH /nfs/farm/g/glast/u/giacomov/diffuseModels
setenv GALACTIC_DIFFUSE_TEMPLATE /afs/slac/g/glast/groups/grb/diffuseModels//template_4years_P8_V2_scaled.fits


#####################################################################
echo '...........................................................................'
echo '..........CONFIGURATION FOR GRBANALYSIS........'
echo '...OS_ARCH..............................:' $OS_ARCH
echo '...INST_DIR.............................:' $INST_DIR
echo '...GTBURST_DIR..........................:' $GTBURST_DIR
echo '...BASEDIR..............................:' $BASEDIR
echo '...PFILES...............................:' $PFILES
#echo '...DIFFUSEMODELS_PATH...................:' $DIFFUSEMODELS_PATH
#echo '...FERMISOURCECATALOG...................:' $FERMISOURCECATALOG
#echo '...GTGRB_USE_PRIOR......................:' $GTGRB_USE_PRIOR
#echo '...BKGE_DATADIR.........................:' $BKGE_DATADIR
echo '...HEADAS...............................:' $HEADAS
echo '...GTBURST_TEMPLATE_PATH................:' $GTBURST_TEMPLATE_PATH
echo '...GALACTIC_DIFFUSE_TEMPLATE............:' $GALACTIC_DIFFUSE_TEMPLATE
echo '...........................................................................' 
echo 'Sourcing the virtual environment for gw studies!'


source /nfs/farm/g/glast/g/grb/gw_environment/setup_gw_conda.csh

