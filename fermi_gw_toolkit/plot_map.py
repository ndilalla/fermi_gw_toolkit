#!/usr/bin/env python

import argparse

from check_file_exists import check_file_exists

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np
from contour_finder import pix_to_sky
from matplotlib import rc
#rc('text', usetex=True)

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
    parser.add_argument('--zscale', help='scale for the color bar',
                        required=False, type=str, default='linear')
    parser.add_argument('--cmap', help='color map for the color bar',
                        required=False, type=str, default='jet')
    parser.add_argument('--rot', help='rotation to center the map',
                        required=False, type=str, default='180,0')
    parser.add_argument('--type', help="'limit' or 'TS'", required=False, type=str,
                        default='limit', choices=['limit','TS'])

    args = parser.parse_args()
    # Read map

    hpx_ul = hp.read_map(args.map)

    # Get nside

    nside = hp.get_nside(hpx_ul)

    # Get some meaningful limits for the color bar among the points which are larger than 0 and finite

    idx = (hpx_ul > 0) & np.isfinite(hpx_ul)

    # Use the provided percentiles

    if args.min_percentile != 0:

        mmin = np.percentile(hpx_ul[idx],args.min_percentile)
        print("%s percentile is %s" % (args.min_percentile, mmin))

    else:

        mmin = hpx_ul.min()

    if args.max_percentile != 100:

        mmax = np.percentile(hpx_ul[idx],args.max_percentile, interpolation='nearest')

        mmax_idx = (hpx_ul == mmax).nonzero()[0][0]

        #print mmax_idx

        ra, dec = pix_to_sky(mmax_idx, nside)

        print("%s percentile is %s, at %s, %s" % (args.max_percentile, mmax, ra, dec))

    else:

        mmax = hpx_ul.max()

    # Now set to nan all negative or zero pixels

    idx = hpx_ul < 0
    hpx_ul[idx] = np.nan
    if args.cmap=='jet':
        background='w'
        background='ivory'
        background='antiquewhite'
        cmap = matplotlib.cm.jet
        cmap.set_under("w",alpha=0) # sets background to white
        cmap.set_bad(background)
        
    elif args.cmap=='afmhot_r':
        cmap = matplotlib.cm.afmhot_r
        cmap.set_bad('#f0f0f0')
        pass
    # Rotation for the mollview map:
    rot=args.rot.split(',')

    fig = plt.figure(figsize=(15, 8))

    # Get order of magnitude of the median (to scale the values)

    if args.type == 'limit':

        magnitude = 10 ** np.floor(np.log10(np.median(hpx_ul[np.isfinite(hpx_ul)])))
        label = r'Upper limit (0.1-1 GeV) [10$^{%.0f}$ erg cm$^{-2}$ s$^{-1}$]' % np.log10(magnitude)

    else:

        magnitude = 1.0
        label = 'LRT Test Statistic'

    projected_map = hp.mollview(hpx_ul / magnitude, rot=rot,
                                min=mmin / magnitude,
                                max=mmax / magnitude,
                                norm=args.zscale,
                                return_projected_map=True, xsize=1000, coord='C',
                                title='',
                                cmap=cmap,
                                fig=1, cbar=None,notext=True)

    ax = plt.gca()
    image = ax.get_images()[0]
    cmap = fig.colorbar(image, ax=ax, cmap=cmap, orientation='horizontal', shrink=0.5,
                        label=label,
                        ticks=np.linspace(mmin / magnitude, mmax / magnitude, 4),
                        format='%.2g')

    hp.graticule()
    lat=0
    for lon in range(60,360,60):
        hp.visufunc.projtext(lon,lat,r'--%d$^{\circ}$' %(lon),lonlat=True,size=15,va='bottom')
        pass

    lon=179.9-float(rot[0])
    for lat in range(-60,90,30):
        if lat==0:
            va='center'
            continue
        elif lat>0:va='bottom'
        else:
            va='top'
        hp.visufunc.projtext(lon,lat, r'%d$^{\circ}$ ' %(lat),lonlat=True,size=15,horizontalalignment='right',va=va)
        pass
    plt.text(-2.2,0,'Dec',rotation=90,size=20)
    plt.text(0,-1.1,'RA',size=20,ha='center')
    
    #for ra in range(-150, 180, 60):
    #    hp.visufunc.projtext(ra + 7.5, -10, '%.0f' % ra, lonlat=True)

    #for dec in range(-60, 90, 30):
    #    hp.visufunc.projtext(7.5, dec - 10, '%.0f' % dec, lonlat=True)

    fig.savefig(args.out_plot)
