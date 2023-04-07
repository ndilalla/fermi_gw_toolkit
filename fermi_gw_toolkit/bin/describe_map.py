#!/usr/bin/env python

import argparse

from check_file_exists import check_file_exists

import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np

if __name__=="__main__":

    desc = '''Describe a map from the statistical point of view (percentiles, minimum, maximum and so on)'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--map',help='Input HEALPIX map', type=check_file_exists, required=True)
    parser.add_argument('--outfile', help='Name for output histogram', type=str, required=True)

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
    print("  * 0   (min)  : %g" % masked.min())
    print("  * 5          : %g" % five)
    print("  * 16         : %g" % sixteen)
    print("  * 50         : %g" % fifty)
    print("  * 84         : %g" % eigthyfour)
    print("  * 90         : %g" % ninety)
    print("  * 95         : %g" % ninetyfive)
    print("  * 100 (max)  : %g" % masked.max())
    print("\nAverage        : %g" % average)
    print("\nStd. dev.      : %g" % std)

    # Now make histograms

    # Compute area of each pixels in square degrees

    pixel_area_sterad = 4.0 * np.pi / (hp.nside2npix(nside))
    pixel_area_sqd = pixel_area_sterad * 3282.8

    # Make histogram in square degrees

    y1 = hpx_ul[np.isfinite(hpx_ul)]

    # Weight each pixel by its area

    w1 = np.zeros_like(y1) + pixel_area_sqd

    # 20 logarithmic bins between min and max

    bins = np.logspace(np.log10(y1[y1 > 0].min()), np.log10(y1.max()), 20)

    # Make the histogram

    # Set the style

    sns.set(color_codes=True)
    sns.set(font_scale=3)

    fig = plt.figure(figsize=(16*3, 8.0*3), dpi=150)

    ax = sns.distplot(y1, bins, kde=False, rug=False,
                      hist_kws={'weights': w1},)
    ax.set_xscale('log')
    ax.set_xlabel(r"flux upper limit (erg cm$^2$ s$^{-1}$)")
    ax.set_ylabel("Solid angle (sq. degrees)")
    ax.set_xlim([bins.min()/2.0,bins.max()*2])
    ax.get_xaxis().get_major_formatter().labelOnlyBase = False

    fig.tight_layout()

    plt.savefig(args.outfile)