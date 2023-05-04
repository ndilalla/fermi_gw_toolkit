#!/usr/bin/env python
import argparse
from fermi_gw_toolkit.utils.check_file_exists import check_file_exists
from fermi_gw_toolkit.lib.contour_finder import ContourFinder,pix_to_sky,sky_to_pix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np
from matplotlib import rc
import matplotlib.cm as cm
from matplotlib.colors import LogNorm, PowerNorm
from matplotlib.ticker import MaxNLocator
#import aplpy
import pyregion
from astropy.wcs import WCS
from astropy.visualization.wcsaxes import WCSAxes
from astropy.io import fits
import scipy as sp
from scipy.ndimage import gaussian_filter
#rc('text', usetex=True)

from astropy import units as u
from astropy.coordinates import SkyCoord

class pgwave_list():
    def __init__(self,filename):
        self.data=np.loadtxt(filename)
        #print(self.data)
        pass
    def get_info(self):
        snr     = self.data[:,6]
        ksig    = self.data[:,7]
        counts  = self.data[:,8]
        return snr,ksig,counts
        
    def get_galactic(self):
        l=self.data[:,3]
        b=self.data[:,4]
        return SkyCoord(l=l*u.degree, b=b*u.degree, frame='galactic')

    def get_celestial(self):
        g=self.get_galactic()
        return g.transform_to('fk5')
    pass

def save_empty(out_filename=None):
    txt='#     [RA]      [DEC]        [L]        [B]      [S/N]     [KSIG]  [COUNTS]  [GWPROB]\n'
    if out_filename is not None: 
        with open(out_filename,'w') as f:
            f.writelines(txt)
    print(txt)
    pass

def save(ra,dec,l,b,snr,ksig,counts,prob,pmin,out_filename=None):
    txt='#     [RA]      [DEC]        [L]        [B]      [S/N]     [KSIG]  [COUNTS]  [GWPROB]\n'
    for r,d,ll,bb,s,k,c,p in zip(ra,dec,l,b,snr,ksig,counts,prob):
        if p>pmin: txt+='%10.3f %10.3f %10.3f %10.3f %10.1f %10.1f %7d %10.1e\n' %(r,d,ll,bb,s,k,c,p)
        pass
    if out_filename is not None: 
        with open(out_filename,'w') as f:
            f.writelines(txt)
    print(txt)
    pass

def galactic(f,ax,l,b,symbol='cross',size=11,color='red',prob=None,pmin=0):
    reg='galactic\n'
    valid=False
    if prob is None:
        for x,y in zip(l,b):
            reg+='point (%f,%f)  # color=%s width=2 point=%s %d\n' %(x,y,color,symbol,size)
            valid=True
            pass
        pass
    else:
        for x,y,p in zip(l,b,prob):
            if p>pmin:
                reg+='point (%f,%f)  # color=%s width=2 point=%s size=%d text={%.1e} font="times 13 bold"\n' %(x,y,color,symbol,size,p)
                valid=True
            pass
        pass
    if valid:
        r1  = pyregion.parse(reg)
        r2  = r1.as_imagecoord(f[0].header)
        patch_list, artist_list = r2.get_mpl_patches_texts()
        for p in patch_list:
            ax.add_patch(p)
            pass
        for t in artist_list:
            ax.add_artist(t)
            pass
        pass
    pass

if __name__=="__main__":
    desc = '''Plot a colormap adding region file'''
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--map',help='Input count map', type=check_file_exists, required=True)
    parser.add_argument('--out',help='Output file name', type=str, required=True)
    parser.add_argument('--regions',help='Region file', type=str, required=False,default=None)
    parser.add_argument('--pgwlist',help='List file', type=str, required=False,default=None)
    parser.add_argument('--smooth',help='Smooth the CMAP using the npix', type=int, required=False,default=0)
    parser.add_argument('--hpmap',help='use the HealPix map to weight the list of sources from pgwave', type=check_file_exists, required=False,default=None)
    parser.add_argument('--pgwoutlist',help='Output List file', type=str, required=False,default=None)

    args = parser.parse_args()
    
    cmap_file = args.map
    regions   = args.regions
    pgwlist   = args.pgwlist
    hpmap     = args.hpmap

    f         = fits.open(cmap_file)
    fig = plt.figure(figsize=(12, 8))

    wcs = WCS(f[0].header)
    ax = WCSAxes(fig, [0.1, 0.1, 0.8, 0.8], wcs=wcs)
    fig.add_axes(ax)

    data=sp.float64(f[0].data)
    if args.smooth>0:
        data=gaussian_filter(data, args.smooth/(2*np.sqrt(2*np.log(2))))
        pass
    mask = np.logical_not(data > 0)
    data[mask] = np.nan
    vmax = np.ceil(np.nanmax(data))
    #axcolor = fig.add_axes([0.9, 0.1, 0.03, 0.8])
    im = ax.imshow(data, cmap=cm.jet, origin="lower", norm=PowerNorm(0.25, vmin=0, vmax=vmax)) #norm=LogNorm(vmin=1e-5*vmax,vmax=vmax))
    plt.text(data.shape[1]/2.,-20,'GAL l',size=20,ha='center')
    plt.text(-20,140,'GAL b',rotation=90,size=20)
    cbar = fig.colorbar(im, orientation='horizontal', pad=0.15, shrink=0.8, label='Counts')
    cbar.ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    #    gc = aplpy.FITSFigure(cmap_file,figure=fig)        
    #    gc.show_colorscale(aspect='auto')
    if regions is not None:
        r  = pyregion.open(regions)
        r2 = r.as_imagecoord(f[0].header)
        patch_list, artist_list = r2.get_mpl_patches_texts()
        for p in patch_list:
            ax.add_patch(p)
            pass
        for t in artist_list:
            ax.add_artist(t)
            pass
        pass
    if pgwlist is not None:
        _list=pgwave_list(pgwlist)
        if len(_list.data) == 0:
            print('WARNING: pgwave candidate source list is empty.')
            print('Saving an empty output list...')
            save_empty(args.pgwoutlist)
        else:
            l_b             = _list.get_galactic()
            ra_dec          = _list.get_celestial()
            snr,ksig,counts = _list.get_info()

            ra=ra_dec.ra.degree 
            dec=ra_dec.dec.degree 
            l=l_b.l.degree
            b=l_b.b.degree 

            if hpmap is not None:
                nside=32
                my_finder = ContourFinder(hpmap,nside)
                hpx       = my_finder.map

                idx       = sky_to_pix(ra,dec, nside)
                prob      = hpx[idx]

                indexes   = my_finder.find_contour(0.9)
                cra,cdec  = pix_to_sky(indexes,nside)

                cel       = SkyCoord(ra=cra*u.degree, dec=cdec*u.degree, frame='fk5')            
                gal       = cel.transform_to('galactic')
                cl,cb     = gal.l.degree,gal.b.degree
                print('plotting countour...%d points' % len(cl))
                galactic(f,ax,cl,cb,symbol='circle',size=1,color='black',prob=None)

                pmin = hpx[indexes].min()
                print(np.sum(hpx),pmin)
            else:
                pmin=0
                prob=None
                pass
            
            print('plotting sources...')
            galactic(f,ax,l,b,symbol='cross',size=11,color='red',prob=None)
            galactic(f,ax,l,b,symbol='circle',size=11,color='red',prob=prob,pmin=pmin)
            if prob is not None:
                save(ra,dec,l,b,snr,ksig,counts,prob,pmin,args.pgwoutlist)
            pass
    fig.savefig(args.out)
