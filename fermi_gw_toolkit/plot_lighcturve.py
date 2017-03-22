#!/usr/bin/env python
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import healpy as hp
import numpy as np
from matplotlib.ticker import NullFormatter
import matplotlib.colors as colors
import matplotlib.cm as cmx

from check_file_exists import check_file_exists
import glob
#from matplotlib import rc
#rc('text', usetex=True)

def sky_to_healpix_id(this_ra, this_dec,nside):

    theta = 0.5 * np.pi - np.deg2rad(this_dec)
    phi = np.deg2rad(this_ra)
    ipix = hp.ang2pix(nside, theta, phi)

    return ipix

def plotOneFile(ax,text_file_name):
    MeV2erg=1.6027e-6

    data = np.recfromtxt(text_file_name, names=True)
    x   = data['median']
    dx0 = x-data['start']
    dx1 = data['end']-x
    y   = data['EnergyFlux']*MeV2erg
    dy  = data['ErrorEF']*MeV2erg
    f=np.logical_and(dy>0,dy<y)
    if x[f].min()<1000:
        ax.errorbar(x[f],y[f],xerr=(dx0[f],dx1[f]),yerr=dy[f],ls='None',capsize=0,linewidth=3,alpha=1)
    print '---->',text_file_name
    print x[f].min(),x[f].max(),y[f]

if __name__=="__main__":
    desc = '''Plot a healpix map in Mollweide projection'''
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--input',help='Input text file containing the pixel information', type=check_file_exists, required=True)
    parser.add_argument('--triggertime',help='Trigger time (MET)', type=float, required=True)
    parser.add_argument('--out_plot',help='Name for the output file (the format will be guessed from the extension)',
                        required=True, type=str)
    parser.add_argument('--tmin',help='minimum time for the x-axis', required=False, default=None)

    parser.add_argument('--tmax',help='maximum time for the x-axis', required=False, default=None)

    parser.add_argument('--lc',help='directory containing the LC files',
                        required=False, default=None)
    parser.add_argument('--nside',help='Input HEALPIX NSIDE', type=int, required=False,default=0)
    parser.add_argument('--xlabel',help='Label of the x axis', type=str, required=False,default="GW")
    #parser.add_argument('--ylabel',help='Label of the y axis', type=str, required=False,default="Flux [erg cm$^{-2}$ s$^{-1}$]")
    parser.add_argument('--histo',help='Horizontal Histogram', type=int, required=False,default=1)
    parser.add_argument('--type',help='Energy flux or photon flux? [EFLUX,FLUX]', type=str, required=False,default='FLUX')

    args = parser.parse_args()
    xlabel='Seconds from t$_{%s}$' % args.xlabel.replace('bn','')
    ylabel="Flux Upper Bound [erg cm$^{-2}$ s$^{-1}$]"
    if args.type=='EFLUX':
        ylabel = "Upper Bound (0.1 - 1 GeV) [erg cm$^{-2}$ s$^{-1}$]"
        ylabel = "Upper Bound [erg cm$^{-2}$ s$^{-1}$]"
    else:
        ylabel = "Upper Bound (0.1 - 1 GeV) [cm$^{-2}$ s$^{-1}$]"
        ylabel = "Upper Bound [cm$^{-2}$ s$^{-1}$]"
        pass

    ##################################################
    # READ THE DATA:
    ##################################################
    data = np.recfromtxt(args.input, names=True)
    triggertime=args.triggertime
    
    #start    = data['met']-triggertime+data['t0']
    #duration = data['t1']
    #end      = start+duration
    #center   = (start+end)/2.
    #flux     = data['flux']#*1e10
    #flux_err = data['flux_err']#*1e10
    #ra       = data['ra']
    #dec      = data['dec']
    #pos      = data['pos']
    start    = data['tstart']-triggertime
    end      = data['tstop']-triggertime
    duration = end-start
    center   = (start+end)/2.
    flux_c     = data['flux']#*1e10
    flux_err_c = data['fluxError']#*1e10
    ra       = data['ra']
    dec      = data['dec']
    flux=[]
    flux_err=[]
    for i,f in enumerate(flux_c):
        if '<' in f: flux.append(float(f.replace('<','')))
        else: flux[i]=f.append(float(f))
        pass
    for i,ef in enumerate(flux_err_c):
        if 'n.a.' in ef: flux_err.append(0.0)
        else: flux_err.append(float(ef))
        pass
    flux=np.array(flux)
    flux_err=np.array(flux_err)

    print flux,flux_err

    if args.nside:
        healpix_map = np.zeros(hp.nside2npix(args.nside))*np.nan
        idx         = sky_to_healpix_id(ra,dec,args.nside)
        for i,t in zip(idx,start):
            healpix_map[i]=t
            pass
        pass
    Npoints=len(start)
    ymin=0.9*flux[flux>0].min()
    ymax=1.1*flux.max()
    tmin=start.min()
    tmax=end.max()
    if args.tmin is not None: tmin=float(args.tmin)
    if args.tmax is not None: tmax=float(args.tmax)

    print ' YMIN,YMAX=',ymin,ymax
    print ' TMIN,TMAX=',tmin,tmax

    ##################################################
    fig = plt.figure(figsize=(15, 15),facecolor='w')
    # definitions for the axes
    
    if args.histo:
        print 'displaying the horizontal histogram'
        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.3
        bottom_h = left_h = left + width + 0.02
    else:
        left, width = 0.1, 0.8
        bottom, height = 0.1, 0.3
        bottom_h = left_h = left + width + 0.02
        pass
    rect_scatter = [left, bottom, width, height]
    rect_histx   = [left, bottom_h, width, 0.2]
    rect_histy   = [left_h, bottom, 0.2, height]
    ##################################################
    # LIGHTCURVE:
    # THIS IS THE LIGHTCURVE FRAME
    axLC = plt.axes(rect_scatter)
    plt.yscale('log')
    axLC.set_xlabel(xlabel,size=25)
    axLC.set_ylabel(ylabel,size=25)
    plt.xticks(size=25)
    plt.yticks(size=25)
    
    background='w'
    background='ivory'
    background='antiquewhite'
    cmap = plt.get_cmap('jet')
    #cmap = plt.get_cmap('brg')
    #cmap = plt.get_cmap('plasma')
    #cmap = plt.get_cmap('viridis')
    
    cmap.set_under('w') # sets background to white
    cmap.set_bad(background) # sets background to white
    #vmin=start.min()
    #vmax=start.max()
    vmin=tmin
    vmax=tmax
    
    cNorm  = colors.Normalize(vmin=vmin, vmax=vmax)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    colors=scalarMap.to_rgba(start)
    print len(flux),len(flux_err)
    axLC.errorbar(center,flux,xerr=(duration/2.,duration/2.),yerr=flux_err,ls='None',capsize=0,color=colors,linewidth=3,alpha=1)
    axLC.set_ylim((ymin, ymax))
    axLC.set_xlim((tmin, tmax))
    # THIS IS THE COLORBAR ON THE TOP OF THE LC
    thickness=0.05
    ax2 = fig.add_axes([left, height+0.1, width, thickness])
    plt.xticks(size=20)
    
    cb1 = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap,norm=cNorm,orientation='horizontal',ticklocation='top')
    cb1.set_label(xlabel,size=25)
    ax2.xaxis.set_label_coords(0.05, 1.5)

    cb1.ax.tick_params(labelsize=25)
    if args.lc is not None:
        file_list=glob.glob('%s/*' %args.lc)
        print file_list 
        for f in file_list:
            plotOneFile(axLC,f)
            pass
        pass
    if args.histo:
        # THIS IS THE HISTOGRAM
        #axHistx = plt.axes(rect_histx)
        axHisty = plt.axes(rect_histy)
        plt.yscale('log')
        # no labels
        nullfmt = NullFormatter()  
        #axHistx.xaxis.set_major_formatter(nullfmt)
        axHisty.yaxis.set_major_formatter(nullfmt)
        h,b,p=axHisty.hist(flux,bins=np.logspace(np.log10(ymin),np.log10(ymax),20), orientation='horizontal',color='grey')#np.logspace(np.log10(ymin),np.log10(ymax),20))
        axHisty.set_ylim((ymin, ymax))
        plt.xticks(range(0, int(max(h)),100),size=25)
        #plt.yticks(size=20)
        #ticks=np.linspace(data['ra'].min(),data['ra'].max(),10)
        #ticks=np.linspace(start.min(),start.max(),3)
        pass
    ##################################################
    # THIS IS THE SKYMAP ON TOP:
    # THIS IS THE SKYMAP:
    #axSM = plt.axes(rect_histx)
    ticks_size=25
    if args.nside:
        hp.mollview(healpix_map, title='',cmap=cmap,norm='lin',min=vmin,max=vmax,rot=(180,0),sub=211,cbar=False)
        hp.graticule()
        ax = plt.gca()
        lat=0
        for lon in range(60,360,30):
            hp.projtext(lon,lat,'%d$^{\circ}$' %(lon),lonlat=True,size=ticks_size,va='bottom')
            pass
        
        lon=179.9+180
        for lat in range(-60,90,15):
            if lat==0:
                va='center'
                continue
            elif lat>0:
                va='bottom'
            else:
                va='top'
                pass
            hp.projtext(lon,lat, r'%d$^{\circ}$ ' %(lat),lonlat=True,size=ticks_size,horizontalalignment='right',va=va)

            pass
        #plt.text(-2.2,0,'Dec',rotation=90,size=20)
        #plt.text(0,-1.1,'RA',size=20,ha='center')
        pass

    #print dir(cb1)

    #cbar = fig.colorbar(axLC, ticks=ticks, orientation='horizontal')
    #cbar.ax.set_xticklabels(ticks)  # horizontal colorbar
    print duration[duration>0].min(),duration.max()
    # adding the GRB LAT Lighcturve
    # THIS IS THE SKYMAP ON TOP:
    fig.savefig(args.out_plot)
    #plt.show()
    
