#!/usr/bin/env python

import argparse

from check_file_exists import check_file_exists

import matplotlib
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np

if __name__=="__main__":

    desc = '''Plot a healpix map in Mollweide projection'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--map',help='Input HEALPIX map', type=check_file_exists, required=True)
    parser.add_argument('--out_plot',help='Name for the output file (the format will be guessed from the extension)',
                        required=True, type=str)
    parser.add_argument('--min_percentile', help='Percentile to use as minimum for color bar',
                        required=True, type=str)
    parser.add_argument('--max_percentile', help='Percentile to use as maximum for color bar',
                        required=True, type=str)

    args = parser.parse_args()

    # Read map

    hpx_ul = hp.read_map(args.map)

    # Get nside

    nside = hp.get_nside(hpx_ul)

    # Get some meaningful limits for the color bar among the points which are larger than 0 and finite

    idx = (hpx_ul > 0) & np.isfinite(hpx_ul)

    # Use the 5 and 95 percentile

    mmin = np.percentile(hpx_ul[idx],args.min_percentile)
    mmax = np.percentile(hpx_ul[idx],args.max_percentile)

    # Now set to nan all negative or zero pixels

    idx = hpx_ul <= 0
    hpx_ul[idx] = np.nan

    cmap = matplotlib.cm.afmhot_r
    cmap.set_bad('#f0f0f0')

    fig = plt.figure(figsize=(15, 8))

    # Get order of magnitude of the median (to scale the values)

    magnitude = 10 ** np.floor(np.log10(np.median(hpx_ul[np.isfinite(hpx_ul)])))

    projected_map = hp.mollview(hpx_ul / magnitude, rot=(0, 0),
                                min=mmin / magnitude,
                                max=mmax / magnitude,
                                norm='linear',
                                return_projected_map=True, xsize=1000, coord='C',
                                title='',
                                cmap=cmap,
                                fig=1, cbar=None)

    ax = plt.gca()
    image = ax.get_images()[0]
    cmap = fig.colorbar(image, ax=ax, cmap=cmap, orientation='horizontal', shrink=0.5,
                        label=r'Upper limit (0.1-1 GeV) [10$^{%.0f}$ erg cm$^{-2}$ s$^{-1}$]' % np.log10(magnitude),
                        ticks=np.linspace(mmin / magnitude, mmax / magnitude, 4),
                        format='%.2g')

    hp.graticule()

    for ra in range(-150, 180, 60):
        hp.visufunc.projtext(ra + 7.5, -10, '%.0f' % ra, lonlat=True)

    for dec in range(-60, 90, 30):
        hp.visufunc.projtext(7.5, dec - 10, '%.0f' % dec, lonlat=True)

    fig.savefig(args.out_plot)