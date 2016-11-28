#!/usr/bin/env python

__description__ = 'Transform an FT1 and an FT2 into a package for gtburst'

from check_file_exists import check_file_exists
from GtBurst.dataHandling import _makeDatasetsOutOfLATdata
import sys
import os, shutil
import argparse

try:
    
    from astropy.io.fits import pyfits

except:
    
    import pyfits

"""Command-line switches.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument('--ft1', help='Input FT1 file (already filtered)',
                    type=check_file_exists, required=True)
parser.add_argument('--ft2', help='Input FT2 file', type=check_file_exists,
                    required=True)
parser.add_argument('--triggertime', help='Trigger time in MET', type=float,
                    required=True)
parser.add_argument('--triggername', help='Trigger name', type=str,
                    required=True)
parser.add_argument("--ra", help="R.A. of the object (J2000)", type=float,
                    default=0.0)
parser.add_argument("--dec", help="Dec. of the object (J2000)", type=float,
                    default=0.0)
parser.add_argument("--outdir", help="Output directory", type=str, default='.')

def rawdata2package(**kwargs):
    """Transform an FT1 and an FT2 downloaded from the Data server
       into a package for gtburst.
    """
    
    ft1 = kwargs['ft1']
    ft2 = kwargs['ft2']
    triggertime = kwargs['triggertime']
    triggername = kwargs['triggername']
    ra = kwargs['ra']
    dec = kwargs['dec']
    outdir = str(kwargs['outdir'])
    
    # Rename ft1 and ft2
    new_ft1 = os.path.join(outdir, 'gll_ft1_tr_%s_v00.fit' % triggername)
    new_ft2 = os.path.join(outdir, 'gll_ft2_tr_%s_v00.fit' % triggername)
    
    shutil.copy(ft1, new_ft1)
    shutil.copy(ft2, new_ft2)
    
    # Get start and stop from ft1
    tstart = pyfits.getval(new_ft1,'TSTART','EVENTS')
    tstop = pyfits.getval(new_ft1,'TSTOP','EVENTS')
    
    return _makeDatasetsOutOfLATdata(new_ft1,
                              new_ft2,
                              triggername,
                              tstart,
                              tstop,
                              ra,
                              dec,
                              triggertime,
                              outdir,
                              triggertime,
                              triggertime+1000)

if __name__=="__main__":
    args = parser.parse_args()
    rawdata2package(**args.__dict__)
