#!/usr/bin/env python

__description__ = 'Download LAT data from the Data Catalog at SLAC'

import os
import ast
import argparse

from fermi_gw_toolkit.utils.run_at_slac import run_at_slac

"""Command-line switches.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument("--outdir", help="Output directory for LAT data", type=str,
                    default='.')
parser.add_argument("--tstart", help="Start time in MET", type=float,
                    required=True)
parser.add_argument("--tstop", help="Stop times in MET", type=float,
                    required=True)
parser.add_argument("--padding", help="Padding to start and stop times.",
                    type=float, default=30.)
parser.add_argument('--one_sec', help='Download the one-second FT2 file',
                    type=ast.literal_eval, choices=[True, False], default=True)

def download_LAT_data(**kwargs):

    if not run_at_slac():
        print('ERROR: You can run this application only at SLAC')
        raise RuntimeError
    
    outdir = kwargs['outdir']
    if not os.path.exists(outdir):
        os.system('mkdir -pv %s' % outdir)
    padding = kwargs['padding']
    met_start = kwargs['tstart'] - padding
    met_stop = kwargs['tstop'] + padding
    ft2 = 'FT2'
    if kwargs['one_sec']:
        ft2 = 'FT2SECONDS'
    
    cmd = f'getLATFitsFiles.py --wdir {outdir} --outfile {outdir}/FT1.fits' \
          f' --minTimestamp {met_start} --maxTimestamp {met_stop} --type FT1'\
          f' --verbose 1 --overwrite 1' % locals()
    print('About to run: ', cmd)
    try:
        os.system(cmd)
    except:
        print('ERROR: impossible to run getLATFitsFiles.py')
        print('Are you sure to have installed astrowrap and added it to your PATH?')
    cmd = f'getLATFitsFiles.py --wdir {outdir} --outfile {outdir}/FT2.fits' \
          f' --minTimestamp {met_start} --maxTimestamp {met_stop} --type {ft2}'\
          f' --verbose 1 --overwrite 1' % locals()
    print('About to run: ', cmd)
    try:
        os.system(cmd)
    except:
        print('ERROR: impossible to run getLATFitsFiles.py')
        print('Are you sure to have installed astrowrap and added it to your PATH?')


if __name__=="__main__":
    args = parser.parse_args()
    download_LAT_data(**args.__dict__)
