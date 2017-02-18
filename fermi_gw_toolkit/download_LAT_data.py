#!/usr/bin/env python

__description__ = 'Download LAT data from the Astro Server'

from fermi_gw_toolkit.check_file_exists import check_file_exists
from GtBurst import IRFS
#from scripts.getLATFitsFiles import getFilesAstroServer
from fermi_gw_toolkit.getLATFitsFiles import getFilesAstroServer

import sys
import os, shutil
import ast
import argparse

irf_list = IRFS.IRFS.keys()
#irfs.append('auto')

"""Command-line switches.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument("triggername", help="Trigger name", type=str)
parser.add_argument("--outdir", help="Output directory for LAT data", type=str,
                    default='.')
parser.add_argument("--tstart", help="Start time in MET", type=float,
                    required=True)
parser.add_argument("--tstop", help="Stop times in MET", type=float,
                    required=True)
parser.add_argument("--padding", help="Padding to start and stop times.",
                    type=float, default=30.)
parser.add_argument("--emin", help="Minimum energy for the analysis",
                    type=float, default=100.0)
parser.add_argument("--emax", help="Maximum energy for the analysis",
                    type=float, default=100000.0)
parser.add_argument("--irf", help="Instrument Function to be used (IRF)",
                    type=str, choices=irf_list, required=True)
parser.add_argument('--one_sec', help='Download the one-second FT2 file',
                    type=ast.literal_eval, choices=[True, False], default=True)

def download_LAT_data(**kwargs):
    
    triggername = kwargs['triggername']
    myIRF = IRFS.IRFS[kwargs['irf'].upper()]
    irfs= myIRF.name
    evclass=myIRF.evclass
    outdir = os.path.join(kwargs['outdir'], triggername)
    #if not os.path.exists(outdir):
    #    os.system('mkdir -pv %s' % outdir)
    METStart = kwargs['tstart']
    METStop = kwargs['tstop']
    padding = kwargs['padding']
    one_sec = kwargs['one_sec']
    
    # Retriving the files from the astroserver:
    reprocessingVersion=myIRF.reprocessingVersion.split(',')[-1]
    ASTROSERVER_REPOSITORY = '%s_P%s' %\
                                    (myIRF.name[:2].upper(),reprocessingVersion)

    if 'TRANSIENT' in irfs:
        Astroserver = ASTROSERVER_REPOSITORY + '_ALL'
    else:
        Astroserver = ASTROSERVER_REPOSITORY + '_BASE'

    print 'USING THE ASTROSERVER:'
    print triggername
    print Astroserver
    print 'One second: %s' %one_sec

    return getFilesAstroServer(triggername, METStart-padding, METStop+padding,
                               outdir, OneSec=one_sec, emin=kwargs['emin'],
                               emax=kwargs['emax'], sample=Astroserver,
                               ResponseFunction=irfs, chatter=1)

if __name__=="__main__":
    args = parser.parse_args()
    download_LAT_data(**args.__dict__)
