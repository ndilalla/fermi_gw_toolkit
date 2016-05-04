#!/usr/bin/env python

__author__ = 'giacomov'

import astropy.io.fits as pyfits
import healpy as hp
import numpy as np
import argparse
import os, sys
import matplotlib.pyplot as plt

from GtBurst.angularDistance import getAngularDistance

from contour_finder import pix_to_sky

from check_file_exists import check_file_exists


def get_coverage(ft2file, ligo_map_file, met_t1, met_t2, theta_cut=65, zenith_cut=100):

    ft2data = pyfits.getdata(ft2file)

    ligo_map = hp.read_map(ligo_map_file)

    ligo_ra, ligo_dec = pix_to_sky(range(ligo_map.shape[0]), 512)

    # Filter out pixels with too low probability to gain speed

    interesting_idx = (ligo_map > 1e-7)

    print("Kept %s pixels for considerations in LIGO map" % np.sum(interesting_idx))

    # Loop over the FT2 file and compute the coverage at each time

    start = ft2data.field('START')
    stop = ft2data.field('STOP')

    idx = (start >= met_t1 ) & (stop < met_t2)

    start = start[idx]
    ra_scz = ft2data.field("RA_SCZ")[idx]
    dec_scz = ft2data.field("DEC_SCZ")[idx]

    ra_zenith = ft2data.field("RA_ZENITH")[idx]
    dec_zenith = ft2data.field("DEC_ZENITH")[idx]

    coverage = np.zeros_like(start)

    for i, (t, rz, dz,rz2,dz2) in enumerate(zip(start,ra_scz,dec_scz,ra_zenith,dec_zenith)):

        # Get the angular distance between the current pointing and
        # all the LIGO pixels

        d = getAngularDistance(rz,dz, ligo_ra[interesting_idx], ligo_dec[interesting_idx])

        zenith = getAngularDistance(rz2,dz2, ligo_ra[interesting_idx], ligo_dec[interesting_idx])

        # Select the LIGO pixels within the LAT FOV

        idx = (d < theta_cut) & (zenith < zenith_cut)

        coverage[i] = np.sum(ligo_map[interesting_idx][idx])

        sys.stdout.write("\r%.1f percent completed" % ( (i+1) / float(coverage.shape[0]) * 100.0 ))

    sys.stdout.write("\n")

    return start, coverage

if __name__=="__main__":

    desc = '''Compute the LAT coverage of the LIGO map'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--in_map',help='Input LIGO HEALPIX map', type=check_file_exists, required=True)
    parser.add_argument('--ft2',help='Input FT2 file',
                        type=check_file_exists,required=True)
    parser.add_argument('--start_time',help='Start of time interval (will be used as trigger time)',
                        type=float, required=True)
    parser.add_argument('--stop_time',help='Stop of time interval', type=float, required=True)
    parser.add_argument('--theta_cut',help=('Maximum off-axis angle for the point to be considered within the '+
                                           'field of view'), type=float, required=True)
    parser.add_argument('--zenith_cut',help='Maximum Zenith angle for a point to be considered observable',
                        type=float, required=True)
    parser.add_argument('--outfile',help='Name for the output file',required=True,type=str)

    args = parser.parse_args()

    t, c = get_coverage(args.ft2, args.in_map, args.start_time, args.stop_time, args.theta_cut, args.zenith_cut)

    fig = plt.figure()

    plt.plot(t - args.start_time, c * 100.0,'-',linewidth=2)
    plt.xlabel("Time since trigger (s)",fontsize=18)
    plt.ylabel("Coverage of LIGO map (%)",fontsize=18)
    plt.ylim([0,110])
    _ = plt.yticks(np.arange(0,120,20))
    plt.axhline(100,linestyle=':',color='green')

    plt.savefig(args.outfile)
