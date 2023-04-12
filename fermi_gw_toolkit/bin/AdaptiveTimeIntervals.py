#!/usr/bin/env python
__author__ = 'omodei'

import argparse
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.cm as cmx
from matplotlib import pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
import healpy as hp
import scipy as sp
import numpy as np
from fermi_gw_toolkit.lib.FT2 import FT2
from fermi_gw_toolkit.lib import contour_finder
from fermi_gw_toolkit.utils.check_file_exists import check_file_exists

__description__  = '''Create a text file with start and stop times for time adaptive interval'''

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument('--in_map', help='Input HEALPIX map', type=check_file_exists,
                    required=True)
parser.add_argument('--triggertime', help='MET of the trigger time', type=float,
                    required=True)
parser.add_argument('--nside', help='New NSIDE to degrade the HELPIX map',
                    type=int, required=False, default=32)
parser.add_argument('--cl',
                    help='Containment level for the contour (default: 0.9, i.e., 90 percent)', default=0.9, type=float)

parser.add_argument('--ft2', help='ft2 files', type=str, required=True)
parser.add_argument('--roi', help='Radius of the Region Of Interest (deg)',
                    type=float, required=False, default=0)
parser.add_argument('--theta_cut', help='Maximum off axis angle theta (deg)',
                    type=float, required=False, default=70)
parser.add_argument('--zenith_cut', help='Maximum Zenith Angle (deg)',
                    type=float, required=False, default=100)
parser.add_argument('--output', help='Output text file with starts and tstop (relative to met)',
                    type=str,required=False, default='output.txt')
parser.add_argument('--plot',help='Plot the results (0 or 1)', type=int,
                    required=False, default=0, choices=[0,1])

def sky_to_pix(ra,dec, nside):
    """Convert the pixels corresponding to sky coordinates (RA, Dec) into input indexes """
    phi   = np.deg2rad(ra)
    theta = 0.5 * np.pi-np.deg2rad(dec)
    #dec = np.rad2deg(0.5 * np.pi - theta)
    return hp.ang2pix(nside, theta, phi)


def adaptive_time(**kwargs):
    # Convenient names
    healpix_map = kwargs['in_map']
    nside       = kwargs['nside']
    ft2         = kwargs['ft2']
    roi         = kwargs['roi']
    triggertime = kwargs['triggertime']
    theta_max   = kwargs['theta_cut']
    zenith_max  = kwargs['zenith_cut']
    output      = kwargs['output']
    plot        = kwargs['plot']

    orgx        = 0
    orgy        = 0

    my_finder = contour_finder.ContourFinder(healpix_map, nside)
    

    print("The intermediate map has an average pixel size of %.3f deg" % my_finder.pixel_size)

    indexes = my_finder.find_contour(kwargs['cl'])

    Nselected = indexes.shape[0]
    print("Found %s points within the %s percent containment level" % (Nselected, kwargs['cl'] * 100.0))
    
    ligo_map=my_finder.map
    print(Nselected, len(ligo_map))
    ligo_selected = np.zeros(len(ligo_map))
    ligo_entry    = np.zeros(len(ligo_map))
    ligo_expo     = np.zeros(len(ligo_map))

    # Get R.A. and Dec for the pixels within the contour
    masked_ra, masked_dec = my_finder.get_sky_coordinates(indexes)

    masked_radius = my_finder.pixel_size

    if roi: masked_radius=roi
    
    print('Number of selected pixels:', Nselected)
    myFT2=FT2(ft2)    
    myFT2.fov(theta_max-masked_radius,zenith_max-masked_radius)
    times_t0=[]
    times_t1=[]
    txt='# RA     Dec      T_enter      T_exit      Delta_T\n'
    #######################################
    for i in range(Nselected):
        entry_time,exit_time=myFT2.getEntryExitTime(masked_ra[i],masked_dec[i],triggertime)
        pix=indexes[i]
        expo_time=exit_time-entry_time
        #print(i,pix,masked_ra[i],masked_dec[i],entry_time,expo_time)
        ligo_entry[pix]=entry_time
        ligo_expo[pix]=expo_time
        ligo_selected[pix]=1
        times_t0.append(entry_time)
        times_t1.append(exit_time)
        #print('i/N:%7d/%7d pix:%7d ra:%10.3f dec:%10.3f entry:%10.3f exit:%10.3f exposure:%10.3f' %(i,Nselected,pix,masked_ra[i],masked_dec[i],entry_time,exit_time,expo_time))
        txt+='%10.3f %10.3f %10.3f %10.3f %10.3f\n' %(masked_ra[i],masked_dec[i],entry_time,exit_time,exit_time-entry_time)
        # a=raw_input('')
        pass
    times_t0=np.array(times_t0)
    times_t1=np.array(times_t1)
    
    with open(output, 'w') as outfile:
        outfile.writelines(txt)
    
    if plot:
        p_max=ligo_map.max()
        fig=plt.figure(figsize=(20,10),facecolor='w')
        idx = ligo_entry == 0
        ligo_entry[idx] = np.nan
        #idx = ligo_expo == 0
        #ligo_expo[idx] = np.nan

        jet = plt.get_cmap('jet')
        #jet = colors.Colormap('jet')
        cNorm  = colors.Normalize(vmin=times_t0.min(), vmax=times_t0.max())
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

        cool_cmap = cm.jet
        cool_cmap.set_under("w") # sets background to white
        cool_cmap.set_bad("w") # sets background to white
        #cb1 = mpl.colorbar.ColorbarBase(ax2, cmap=jet,norm=cNorm,orientation='horizontal')
        #cb1.set_label ('Time since LIGO trigger [s]')
        rot=(orgx,orgy)
        hp.mollview(ligo_map/p_max, sub=221, title='Ligo Map',cmap=cool_cmap,rot=rot)
        hp.graticule()
        hp.mollview(ligo_selected, sub=222, title='Ligo Map (%.1f c.l.)' % kwargs['cl'],cmap=cool_cmap,norm='lin',min=0,max=1.0,rot=rot)
        hp.graticule()
        hp.mollview(ligo_entry, sub=223, title='Entry Time',cmap=jet,norm='lin',min=times_t0.min(),max=times_t0.max(),rot=rot)
        hp.graticule()
        hp.mollview(ligo_expo, sub=224, title='Exposure (s)',cmap=cool_cmap,norm='log',min=0.1,max=max(ligo_expo),rot=rot)
        hp.graticule()
        ax = plt.gca()
        plot_file=output.replace('.txt','_coverage_map.png')
        print('Saving plot to: %s' % plot_file)
        fig.savefig(plot_file)
        #plt.show()
        pass
    pass

# --------------------- #
    
if __name__=="__main__":
    args = parser.parse_args()
    adaptive_time(**args.__dict__)
