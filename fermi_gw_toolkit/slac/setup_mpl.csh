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
setenv BLDTYPE ${OS_ARCH}-Optimized
setenv INST_DIR /nfs/farm/g/glast/u35/ReleaseManagerBuild/${OS_ARCH}/Optimized/ScienceTools/11-05-01
setenv GLAST_EXT /afs/slac/g/glast/ground/GLAST_EXT/${OS_ARCH}
source $INST_DIR/bin/$BLDTYPE/_setup.csh
setenv FISHEYEDIR /afs/slac/g/glast/groups/solar/omodei/Sun/fisheye/
# Diffuse models for pass7 & Pass8
setenv DIFFUSEMODELS_PATH '/afs/slac/g/glast/groups/grb/diffuseModels/'
# FERMI SOURCE CATALOG                                                                                                                                         
setenv FERMISOURCECATALOG '/afs/slac/g/glast/groups/grb/DATA/CATALOGS/gll_psc_v08.fit'
