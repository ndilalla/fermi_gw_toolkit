#!/usr/bin/env python

__author__ = 'giacomov'

import argparse
import sys

import astropy.io.fits as pyfits
import healpy as hp
import matplotlib.pyplot as plt
import numpy as np

from GtBurst.angularDistance import getAngularDistance

from check_file_exists import check_file_exists
from contour_finder import pix_to_sky

__description__ = '''Compute the LAT coverage of the LIGO map'''

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument('--in_map', help='Input LIGO HEALPIX map', type=check_file_exists, required=True)
parser.add_argument('--ft2', help='Input FT2 file',
                    type=check_file_exists, required=True)
parser.add_argument('--start_time', help='Start of time interval (will be used as trigger time)',
                    type=float, required=True)
parser.add_argument('--stop_time', help='Stop of time interval', type=float, required=True)
parser.add_argument('--theta_cut', help=('Maximum off-axis angle for the point to be considered within the ' +
                                         'field of view'), type=float, required=True)
parser.add_argument('--zenith_cut', help='Maximum Zenith angle for a point to be considered observable',
                    type=float, required=True)
parser.add_argument('--outroot', help='Root for the names of the output files', required=True, type=str)
parser.add_argument('--vert_lines', help='Positions for vertical lines in the plot',
                    default=[], type=float, nargs='+')

def _gtmktime(ft2data, met_t1, met_t2, cadence):
    # This is the equivalent of gtmktime, more or less


    # Loop over the FT2 file and compute the coverage at each time

    data_qual = ft2data.field("DATA_QUAL")
    lat_config = ft2data.field("LAT_CONFIG")
    in_saa = ft2data.field("IN_SAA")
    livetime = ft2data.field("LIVETIME")

    start = ft2data.field('START')
    stop = ft2data.field('STOP')

    # (DATA_QUAL>0 || DATA_QUAL==-1) && LAT_CONFIG==1 && IN_SAA!=T && LIVETIME>0

    idx = ((start >= met_t1) & (stop < met_t2) &
           ((data_qual > 0) | (data_qual == -1)) &
           (lat_config == 1) & (in_saa != 1) & (livetime > 0))

    start = start[idx][::cadence]
    ra_scz = ft2data.field("RA_SCZ")[idx][::cadence]
    dec_scz = ft2data.field("DEC_SCZ")[idx][::cadence]

    ra_zenith = ft2data.field("RA_ZENITH")[idx][::cadence]
    dec_zenith = ft2data.field("DEC_ZENITH")[idx][::cadence]

    return start, ra_scz, dec_scz, ra_zenith, dec_zenith


def get_coverage(ft2file, ligo_map_file, met_t1, met_t2, theta_cut, zenith_cut):
    ft2data = pyfits.getdata(ft2file)

    ligo_map = hp.read_map(ligo_map_file)

    ligo_ra, ligo_dec = pix_to_sky(range(ligo_map.shape[0]), 512)

    # Filter out pixels with too low probability to gain speed

    interesting_idx = (ligo_map > 1e-7)

    print("Kept %s pixels for considerations in LIGO map" % np.sum(interesting_idx))

    # Get entries from the FT2 file every 10 s (cadence)

    start, ra_scz, dec_scz, ra_zenith, dec_zenith = _gtmktime(ft2data, met_t1, met_t2, cadence=30)

    print("\nCoverage will be computed from %.1f to %.1f\n" % (start.min(), start.max()))

    coverage = np.zeros_like(start)

    for i, (t, rz, dz, rz2, dz2) in enumerate(zip(start, ra_scz, dec_scz, ra_zenith, dec_zenith)):
        # Get the angular distance between the current pointing and
        # all the LIGO pixels

        d = getAngularDistance(rz, dz, ligo_ra[interesting_idx], ligo_dec[interesting_idx])

        zenith = getAngularDistance(rz2, dz2, ligo_ra[interesting_idx], ligo_dec[interesting_idx])

        # Select the LIGO pixels within the LAT FOV

        idx = (d < theta_cut) & (zenith < zenith_cut)

        coverage[i] = np.sum(ligo_map[interesting_idx][idx])

        sys.stdout.write("\r%.1f percent completed" % ((i + 1) / float(coverage.shape[0]) * 100.0))

    sys.stdout.write("\n")

    return start, coverage


def get_probability_coverage(ft2file, ligo_map_file, met_t1, met_t2, theta_cut, zenith_cut):

    ft2data = pyfits.getdata(ft2file)

    ligo_map = hp.read_map(ligo_map_file)

    # Probe NSIDE
    nside = hp.get_nside(ligo_map)

    # Get entries from the FT2 file every 10 s (cadence)

    start, ra_scz, dec_scz, ra_zenith, dec_zenith = _gtmktime(ft2data, met_t1, met_t2, cadence=30)

    coverage = np.zeros_like(start)

    for i, (t, rz, dz, rz2, dz2) in enumerate(zip(start, ra_scz, dec_scz, ra_zenith, dec_zenith)):

        # Find the pixels inside the LAT FoV (theta < theta_cut)

        vec = hp.rotator.dir2vec(rz, dz, lonlat=True)
        idx_z = hp.query_disc(nside, vec, np.deg2rad(theta_cut), inclusive=False)

        # Find the pixels at Zenith angles less
        # than zenith_cut

        vec = hp.rotator.dir2vec(rz2, dz2, lonlat=True)
        idx_z2 = hp.query_disc(nside, vec, np.deg2rad(zenith_cut), inclusive=False)

        # Intersect the two lists of pixels to find pixels which are at the same time
        # inside the FoV and at Zenith < zenith_cut

        idx = np.intersect1d(idx_z, idx_z2)

        # Compute the incremental probability coverage

        coverage[i] = np.sum(ligo_map[idx])

        # Now put the pixel I counted to zero so I don't count them twice
        ligo_map[idx] = 0

        sys.stdout.write("\r%.1f percent completed" % ((i + 1) / float(coverage.shape[0]) * 100.0))

    return start, coverage

def compute_coverage(**kwargs):

    # Try to use seaborn, if installed
    try:

        import seaborn as sns

        sns.set(color_codes=True)
        sns.set(font_scale=3)
        sns.set_style("whitegrid")
        sns.set_style("ticks")

    except:

        print("\n\nWARNING: seaborn is not installed, using normal matplotlib style")


    # Make coverage plot

    t, c = get_coverage(kwargs['ft2'],
                        kwargs['in_map'],
                        kwargs['start_time'],
                        kwargs['stop_time'],
                        kwargs['theta_cut'],
                        kwargs['zenith_cut'])

    #with sns.plotting_context("paper", font_scale=3):

    fig = plt.figure(figsize=(16*3, 8.0*3), dpi=150)

    dt = (t - kwargs['start_time']) / 1000.0

    plt.plot(dt, c * 100.0, '-', linewidth=4)
    plt.xlabel("Time since trigger (ks)")
    plt.ylabel("Coverage of LIGO map (%)")
    plt.ylim([0, 110])
    plt.xlim([dt.min(), dt.max()])
    _ = plt.yticks(np.arange(0, 120, 20))
    plt.axhline(100, linestyle=':', color='green')

    if kwargs['vert_lines']:

        for p in kwargs['vert_lines']:

            plt.axvline(p / 1000.0, linestyle=':', color='black', lw=2)
            plt.text(p / 1000.0, 115, '%.1f ks' % (p / 1000.0), horizontalalignment='center')

    fig.tight_layout()

    print 'Saving plot to: %s_coverage.png' % kwargs['outroot']
    fig.savefig('%s_coverage.png' % kwargs['outroot'])

    # Make cumulative probability plot

    t, c = get_probability_coverage(kwargs['ft2'],
                                    kwargs['in_map'],
                                    kwargs['start_time'],
                                    kwargs['stop_time'],
                                    kwargs['theta_cut'],
                                    kwargs['zenith_cut'])

    sky_coverage = np.cumsum(c)

    dt = (t - kwargs['start_time']) / 1000.0

    fig = plt.figure(figsize=(16*3, 8.0*3), dpi=150)

    plt.plot(dt, sky_coverage, lw=4)

    plt.xlabel("Time since trigger (ks)")
    plt.ylabel("Cumulative\nprobability coverage")

    plt.ylim([0,1.1])
    plt.xlim([dt.min(),dt.max()])
    plt.axhline(1, linestyle=':', color='green')

    if kwargs['vert_lines']:

        for p in kwargs['vert_lines']:
            plt.axvline(p / 1000.0, linestyle=':', color='black', lw=2)
            plt.text(p / 1000.0, 1.11, '%.1f ks' % (p / 1000.0), horizontalalignment='center')

    fig.tight_layout()
    print 'Saving plot to: %s_prob_coverage.png' % kwargs['outroot']
    plt.savefig('%s_prob_coverage.png' % kwargs['outroot'], tight_layout=True)


if __name__ == "__main__":

    args = parser.parse_args()
    compute_coverage(**args.__dict__)
