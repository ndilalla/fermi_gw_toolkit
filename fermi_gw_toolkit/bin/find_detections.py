#!/usr/bin/env python

__author__ = 'giacomov'

import argparse
import numpy as np
import healpy as hp
import scipy.stats

from fermi_gw_toolkit.utils.check_file_exists import check_file_exists
from fermi_gw_toolkit.lib.contour_finder import pix_to_sky, ContourFinder


def Hopkins_method(ts_map_array, ra, dec, fdr, psf_size, N, nside, hopkins_correction=True):

    # Compute the number of correlated pixels, i.e., the number of pixels within a PSF distance
    # NOTE: query_disc gets the *radius* of the disc as input, not the diameter, so we can directly use psf_size
    n_correlated_pixels = len(hp.query_disc(nside, (0, 0, 1), np.deg2rad(psf_size), inclusive=True, fact=4))

    print("Got a map with nside %i. Using a number of correlated pixels of %i" % (nside, n_correlated_pixels))

    # This number should be close to psf_size (within ~1 deg)
    approx_corr_rad = np.sqrt(n_correlated_pixels / np.pi) * np.rad2deg(hp.max_pixrad(nside))

    print("Approx. correlation radius (should be within 1 deg of PSF size): %.2f deg" % approx_corr_rad)

    # This notation follows Clements, Sarkar and Guo (2012):
    # https://web.njit.edu/~wguo/Clements_Sarkar_Guo%202012.pdf

    # Get the corresponding p-values
    # We use here the result from Mattox et al. 1996, that TS is distributed as 0.5 chi2(1 dof)
    p_values = 0.5 * scipy.stats.chi2(1).sf(ts_map_array)  # type: np.ndarray

    # Order the p-values from the smallest to the largest. We use argsort to keep track of the reordering
    sort_idx = p_values.argsort()

    # Find
    # kBH = max
    # {j: P(j) <= j alpha / N}

    alpha_over_N = fdr / N

    # Hopkins adjustement
    if hopkins_correction:

        print("Using Hopkins correction")

        C_N = np.sum(1.0 / np.arange(1, n_correlated_pixels+1))

    else:

        C_N = 1

    threshold = np.arange(1, N+1) * alpha_over_N / C_N

    print("Minimum threshold: %.2g, maximum threshold: %.2g" % (threshold.min(), threshold.max()))

    idx = (p_values[sort_idx] <= threshold)

    # Find the largest p-value satisfying the condition
    if np.sum(idx) == 0:

        # No points above the threshold

        return [], [], []

    else:

        # Detections

        # Find out the last point above the threshold, all points before in the sorted p_values array
        # are considered detection

        rightmost_p_value_below_threshold_idx = idx.nonzero()[0].max()

        points_to_keep_idx = sort_idx[:rightmost_p_value_below_threshold_idx+1]

        return ra[points_to_keep_idx], dec[points_to_keep_idx], ts_map_array[points_to_keep_idx]


    # We claim detections all points


if __name__ == "__main__":

    desc = '''List the significant detections in the TS map by using the Benjamini-Hochberg-Yekuteli method as amended 
    by Hopkins et al. 2001 to account for correlation among the pixels'''

    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=formatter)

    parser.add_argument('--tsmap', help='Input TS map',
                        type=check_file_exists, required=True)
    parser.add_argument('--ligomap', help='Input LIGO map', type=check_file_exists,
                        required=True)
    parser.add_argument('--cl',
                        help='Containment level for the contour (default: 0.9, i.e., 90 percent)', default=0.9,
                        type=float)
    parser.add_argument('--false_detection_rate', help='FDR for the search',
                        type=float, required=False, default=0.01)
    parser.add_argument('--psf_size', help='Radius of the PSF to be used as correlation region in the Hopkins '
                                           'adjustement coefficient C_N (in deg)',
                        default=12.0, type=float)
    parser.add_argument('--use-hopkins', help='If set, uses the Hopkins correction for correlated pixels',
                        action='store_true')

    args = parser.parse_args()

    # Get NSIDE from the TS map
    ts_map_array, header = hp.read_map(args.tsmap, h=True, verbose=False)

    # Get NSIDE
    nside = hp.get_nside(ts_map_array)

    # Compute the contours and get the points within the contour
    my_finder = ContourFinder(args.ligomap, nside)

    indexes = my_finder.find_contour(args.cl)
    ra, dec = my_finder.get_sky_coordinates(indexes)

    N = indexes.shape[0]

    print("Found %s points within the %s percent containment level" % (N, args.cl * 100.0))

    # Apply the FDR threshold

    ra, dec, TS = Hopkins_method(ts_map_array[indexes], ra, dec, args.false_detection_rate,
                                 args.psf_size, N, nside, args.use_hopkins)

    print("Found %i detection(s)" % len(ra))

    for r, d, ts in zip(ra, dec, TS):

        print("(RA, Dec.) = (%.3f, %.3f) (TS = %.2f)" % (r, d, ts))