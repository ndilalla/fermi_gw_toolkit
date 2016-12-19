#!/usr/bin/env python

__author__ = 'giacomov'

import argparse
import numpy as np
import healpy as hp
import warnings

from fermi_gw_toolkit.check_file_exists import check_file_exists
from fermi_gw_toolkit.sky_to_healpix_id import sky_to_healpix_id

desc = '''Fill the input HEALPIX map with the values taken from the input text file'''

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=desc, formatter_class=formatter)

parser.add_argument('--in_map', help='Input HEALPIX map',
                    type=check_file_exists, required=True)
parser.add_argument('--text_file', type=check_file_exists,required=True,
                    help='Input text file (results from the doTimeResolvedLike script of gtburst)')
parser.add_argument('--out_uls_map', type=str, required=True,
                    help='Name for the output upper limits map')
parser.add_argument('--out_ts_map', help='Name for the output TS map',
                    type=str, required=True)

def fill_maps(**kwargs):
    
    data = np.recfromtxt(kwargs['text_file'], names=True)

    # Check that the fluxes are upper limits

    fluxes = data['flux']

    non_uls = filter(lambda x:x.find('<')<0, fluxes)

    if len(non_uls) > 0:

        warnings.warn("\n\n*** Not all the fluxes are upper limits!\n\n")

    # Convert to float

    upper_limits = np.array(map(lambda x:float(x.replace('<','')),fluxes))

    ra = data['ra']
    dec = data['dec']

    # Get the NSIDE from the input healpix map

    hpx_orig, header = hp.read_map(kwargs['in_map'], h=True, verbose=False)

    nside = hp.npix2nside(hpx_orig.shape[0])

    # Generate a new empty map

    upper_limits_map = np.zeros(hp.nside2npix(nside))

    # Now loop over the input fluxes and assign the corresponding pixels

    for this_ra, this_dec, this_upper_limit in zip(ra,dec,upper_limits):

        id = sky_to_healpix_id(nside, this_ra, this_dec)

        upper_limits_map[id] = this_upper_limit

    # Write the upper limit map

    hp.write_map(kwargs['out_uls_map'], upper_limits_map, coord='C')

    # Now the map of TS

    tss = data['TS']

    ts_map = np.zeros(hp.nside2npix(nside))

    # Now loop over the input fluxes and assign the corresponding pixels

    for this_ra, this_dec, this_ts in zip(ra,dec,tss):

        id = sky_to_healpix_id(nside, this_ra, this_dec)

        ts_map[id] = this_ts

    # Write the upper limit map

    hp.write_map(kwargs['out_ts_map'], ts_map, coord='C')

if __name__=="__main__":
    args = parser.parse_args()
    fill_maps(**args.__dict__)
