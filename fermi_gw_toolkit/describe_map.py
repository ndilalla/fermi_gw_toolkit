#!/usr/bin/env python

import argparse

from check_file_exists import check_file_exists

import matplotlib
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np

if __name__=="__main__":

    desc = '''Describe a map from the statistical point of view (percentiles, minimum, maximum and so on)'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--map',help='Input HEALPIX map', type=check_file_exists, required=True)

    args = parser.parse_args()

    # Read map

    hpx_ul = hp.read_map(args.map)

    # Exclude all nans and negative points

    idx = (hpx_ul > 0) & np.isfinite(hpx_ul)

    masked = hpx_ul[idx]

    # Get nside

    nside = hp.get_nside(hpx_ul)

    # Get percentiles
    five, sixteen, fifty, eigthyfour, ninety, ninetyfive = np.percentile(masked, [5, 16, 50, 84, 90, 95])

    # Get average
    average = np.average(masked)

    # Get standard deviation
    std = np.std(masked)

    # Print everything
    print("\nMap %s:" % args.map)
    print("-----------------------------")
    print("\nNside          : %i" % nside)
    print("\nPercentiles:")
    print("  * 5          : %g" % five)
    print("  * 16         : %g" % sixteen)
    print("  * 50         : %g" % fifty)
    print("  * 84         : %g" % eigthyfour)
    print("  * 90         : %g" % ninety)
    print("  * 95         : %g" % ninetyfive)
    print("\nAverage        : %g" % average)
    print("\nStd. dev.      : %g" % std)