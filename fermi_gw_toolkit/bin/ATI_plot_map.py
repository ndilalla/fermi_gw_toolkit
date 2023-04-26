#!/usr/bin/env python

import argparse

from fermi_gw_toolkit.utils.check_file_exists import check_file_exists
from fermi_gw_toolkit.lib.contour_finder import pix_to_sky

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np

#from matplotlib import rc
#rc('text', usetex=True)

if __name__=="__main__":

    desc = '''Plot a healpix map in Mollweide projection'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--map',help='Input HEALPIX map', type=check_file_exists, required=True)
    parser.add_argument('--out_plot',help='Name for the output file (the format will be guessed from the extension)',
                        required=True, type=str)
    parser.add_argument('--min_percentile', help='Percentile to use as minimum for color bar',
                        required=True, type=float)
    parser.add_argument('--max_percentile', help='Percentile to use as maximum for color bar',
                        required=True, type=float)
    parser.add_argument('--zscale', help='scale for the color bar',
                        required=False, type=str, default='linear')
    parser.add_argument('--cmap', help='color map for the color bar',
                        required=False, type=str, default='jet')
    parser.add_argument('--rot', help='rotation to center the map',
                        required=False, type=str, default='180,0')
    parser.add_argument('--zoom', help='zoom in around rot position',
                        required=False, type=int, default=None)
    parser.add_argument('--map_type', help='type of mat to display, EFLUX, FLUX, TS or SIG',
                        required=False, type=str, default='EFLUX')

    args = parser.parse_args()
    # Read map

    hpx_ul = hp.read_map(args.map)

    # Get nside

    nside = hp.get_nside(hpx_ul)

    norm = args.zscale

    # Get some meaningful limits for the color bar among the points which are larger than 0 and finite
    
    idx = (hpx_ul > 0) & np.isfinite(hpx_ul)
    if np.sum(idx)==0: 
        idx = (hpx_ul >= 0) & np.isfinite(hpx_ul)
        norm = 'linear'
        pass
    # Use the provided percentiles
    if args.min_percentile > 0:

        mmin = np.percentile(hpx_ul[idx],args.min_percentile)

    else:

        mmin = hpx_ul[idx].min()

    if args.max_percentile < 100:
        mmax = np.percentile(hpx_ul[idx],args.max_percentile)
    elif args.max_percentile > 100.:
        mmax=hpx_ul[idx].max()*float(args.max_percentile)/100.
    else:
        mmax = hpx_ul[idx].max()

    # Now set to nan all negative or zero pixels
    if 'log' in norm:
        idx = hpx_ul <= 0
        hpx_ul[idx] = np.nan
        pass

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
    elif args.cmap=='copper':
        cmap = matplotlib.cm.copper
        background='antiquewhite'
        cmap.set_bad(background)
        cmap.set_under("w",alpha=0) # sets background to white 
    elif args.cmap=='summer':
        cmap = matplotlib.cm.summer
        background='antiquewhite'
        cmap.set_bad(background)
        cmap.set_under("w",alpha=0) # sets background to white
    elif args.cmap=='Greens':
        cmap = matplotlib.cm.Greens
        background='antiquewhite'
        cmap.set_bad(background)
        cmap.set_under("w",alpha=0) # sets background to white
    # Rotation for the mollview map:
    rot=args.rot.split(',')

    fig = plt.figure(figsize=(15, 8))

    # Get order of magnitude of the median (to scale the values)
    
    if args.map_type == 'EFLUX':
        magnitude = 10 ** np.floor(np.log10(np.median(hpx_ul[np.isfinite(hpx_ul)])))
        z_title  =r'Flux Upper Bound (0.1-1 GeV) [10$^{%.0f}$ erg cm$^{-2}$ s$^{-1}$]' % np.log10(magnitude)
    elif args.map_type == 'FLUX':
        magnitude = 10 ** np.floor(np.log10(np.median(hpx_ul[np.isfinite(hpx_ul)])))
        z_title  =r'Flux Upper Bound (0.1-1 GeV) [10$^{%.0f}$ cm$^{-2}$ s$^{-1}$]' % np.log10(magnitude)
    elif args.map_type == 'TS':
        z_title  =r'TS ' 
        magnitude = 1
    elif args.map_type == 'SIG':
        z_title  =r'$\sigma$ ' 
        magnitude = 1
    else:
        print('Unrecognized map type %s. Use EFLUX, FLUX or TS' % args.map_type)
        exit()
        pass

        
    MAXVALUE= round(np.nanmax(hpx_ul),2)
    px_max  = np.nanargmax(hpx_ul)
    ra_max, dec_max = pix_to_sky(px_max,nside)

    print('Minimum Value = ', hpx_ul[idx].min())
    print('Maximum Value = ', MAXVALUE)
    print('RA,DEC=%f %f MAX= %f' %(ra_max, dec_max, MAXVALUE))


    ticks=np.logspace(np.log10(mmin / magnitude), np.log10(mmax / magnitude), 4),
    if norm == 'linear': 
        norm=None
        ticks=np.linspace(mmin / magnitude, mmax / magnitude, 4),
        #mmin=0
        pass
    print('Normalization of the axis:',norm)
    if args.zoom is None:
        projected_map = hp.mollview(hpx_ul / magnitude, rot=rot,
                                    min=mmin / magnitude,
                                    max=mmax / magnitude,
                                    norm=norm,
                                    return_projected_map=True, xsize=1000, coord='C',
                                    title='',
                                    cmap=args.cmap,
                                    fig=1, cbar=None,notext=True)
    else:        
        projected_map=hp.gnomview(hpx_ul / magnitude, rot=rot, xsize=args.zoom, ysize=args.zoom, reso=1.0,
                                  min=mmin / magnitude,
                                  max=mmax / magnitude,
                                  norm=norm,
                                  return_projected_map=True, coord='C',
                                  title='',
                                  cmap=args.cmap,
                                  fig=1, cbar=None,notext=True)
        pass
    
    ###
    ax = plt.gca()
    image = ax.get_images()[0]
    cmap = fig.colorbar(image, ax=ax, cmap=cmap, orientation='horizontal', shrink=0.5,
                        label=z_title,
                        ticks=ticks,
                        format='%.2g')

    hp.graticule()
    if args.zoom is None:
        lat=0
        for lon in range(60,360,60):
            hp.visufunc.projtext(lon,lat,'%d$^{\circ}$' %(lon),lonlat=True,size=15,va='bottom')
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
            pass
        plt.text(-2.2,0,'Dec',rotation=90,size=20)
        plt.text(0,-1.1,'RA',size=20,ha='center')
        pass
    else:
        lon_0=float(rot[0])
        lat_0=float(rot[1])
        for lat in np.linspace(lat_0 - args.zoom/120.,lat_0 + args.zoom/120.,5):
            hp.visufunc.projtext(round(lon_0),round(lat), r'%d$^{\circ}$ ' %(int(round(lat))),lonlat=True,size=15,horizontalalignment='left',va='center')
            pass
        for lon in np.linspace(lon_0 - args.zoom/120.,lon_0 + args.zoom/120.,5):
            hp.visufunc.projtext(round(lon),round(lat_0), r'%d$^{\circ}$ ' %int(round((lon))),lonlat=True,size=15,horizontalalignment='center',va='bottom')
            pass
        plt.annotate('Dec',xy=(0.3,0.65),rotation=90,size=20,xycoords='figure fraction')
        plt.annotate('R.A.',xy=(0.5,0.25),size=20,ha='center',xycoords='figure  fraction')
        pass
    #for ra in range(-150, 180, 60):
    #    hp.visufunc.projtext(ra + 7.5, -10, '%.0f' % ra, lonlat=True)

    #for dec in range(-60, 90, 30):
    #    hp.visufunc.projtext(7.5, dec - 10, '%.0f' % dec, lonlat=True)
    
    fig.savefig(args.out_plot)
