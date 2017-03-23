#!/usr/bin/env python
import os, glob, argparse
import numpy
import healpy as hp
#import webbrowser
import astropy.io.fits as pyfits
from contour_finder import  pix_to_sky
formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)

def fix_path(local_path):
    _html_home='http://glast-ground.slac.stanford.edu/Decorator/exp/Fermi/Decorate/groups/grb/GWPIPELINE/'
    _nfs_home='/nfs/farm/g/glast/u26/GWPIPELINE'
    return local_path.replace(_nfs_home,_html_home)

parser.add_argument("--triggername", help="Trigger name", type=str,
                    required=True)
parser.add_argument("--triggertime", help="Trigger time", type=float,
                    required=True)
parser.add_argument("--outfile", help="Output file path", type=str,
                    required=False, default=None)
parser.add_argument('--emin', help='Minimum energy', type=float, required=False,
                    default=100.0)
parser.add_argument('--emax', help='Maximum energy', type=float, required=False,
                    default=100000.0)
parser.add_argument("--tstart", help="Start time in MET", type=float,
                    required=True)
parser.add_argument("--tstop", help="Stop time in MET", type=float,
                    required=True)
parser.add_argument("--thetamax", help="Theta cut", type=float, default=65.0)
parser.add_argument("--zmax", help="Zenith cut", type=float, default=100.0)
parser.add_argument("--roi", help="Radius of the Region Of Interest (ROI)",
                    type=float, default=8.0)
parser.add_argument("--irf", help="Instrument Function to be used (IRF)",
                    type=str, default="p8_transient010e")
parser.add_argument("--galactic_model",help="Galactic model", type=str,
                    default="template")
parser.add_argument("--strategy", help="Strategy for Zenith cut",type=str,
                    default='time')
parser.add_argument("--particle_model", help="Particle model",type=str,
                    default="isotr template")
parser.add_argument("--ts_cut", help="Minimum TS for list", type=float,
                    default=16.)
parser.add_argument('--ligo_map', help='Input HEALPIX LIGO map', type=str,
                    required=True)
parser.add_argument("--fti_ts_map", help="FTI TS map path", type=str,
                    required=True)
parser.add_argument("--ati_ts_map", help="ATI TS map path", type=str,
                    required=True)
parser.add_argument("--img_folder", help="Image folder", type=str,
                    required=False, default=".")
parser.add_argument("--template", help="Template", type=str, required=False,
                    default='results_template.html')
parser.add_argument("--styles", help="Css file for style", type=str,
                    required=False, default='styles.css')

content = '''
<tr><td rowspan="2" align="center">TS<br>{}</td><td>Ra</td><td>{}&deg</td></tr>
<tr><td>Dec</td><td>{}&deg</td></tr>
'''

def get_date(ligo_map):
    hdulist = pyfits.open(ligo_map)
    date_obs = hdulist[1].header['DATE-OBS']
    return date_obs[:10], date_obs[11:19]

def load_file(file_path):
    f = open(file_path)
    page = f.read()
    f.close()
    return page

def write_file(text, outfile):
    output = open(outfile, "w")
    output.write(text)
    output.close()
    
def max_ts(map_path, ts_cut):
    ts_map, header = hp.read_map(map_path, h=True)
    header = dict(header)
    nside = header['NSIDE']
    ts_max = round(ts_map.max(),2)
    px_max = numpy.argmax(ts_map)
    ra_max, dec_max = pix_to_sky(px_max,nside)
    # hp.pix2ang(nside, px_max, lonlat=True)
    ra_max = round(ra_max, 2)
    dec_max = round(dec_max, 2)
    ts_list = insert_ts_list(ts_map, ts_cut, nside)
    return ts_max, ra_max, dec_max, ts_list, nside

def insert_ts_list(ts_map, ts_cut, nside):
    ts_px = numpy.argwhere(ts_map>ts_cut)
    table = ""
    for px in ts_px.T[0]:
        ts = round(ts_map[px],2)
        ra, dec = pix_to_sky(px,nside)
        #ra, dec = hp.pix2ang(nside, px, lonlat=True)
        ra = round(ra, 2)
        dec = round(dec, 2)
        table += content.format(ts, ra, dec)
    return table
    
def show_results(**kwargs):
    web_page = load_file(kwargs['template'])
    styles = load_file(kwargs['styles'])
    
    #define all the variables to be used in the template
    triggername = kwargs['triggername'].replace('bn','')
    triggertime = kwargs['triggertime']
    date, time = get_date(kwargs['ligo_map'])
    emin = kwargs['emin']
    emax = kwargs['emax']
    tstart = kwargs['tstart']
    tstop = kwargs['tstop']
    thetamax = kwargs['thetamax']
    zmax = kwargs['zmax']
    roi = kwargs['roi']
    irf = kwargs['irf']
    gal_model = kwargs['galactic_model']
    strategy = kwargs['strategy']
    part_model = kwargs['particle_model']
    
    #get all the plot from the image folder
    img_folder = kwargs['img_folder']
    coverage_name = 'bn'+triggername +'_prob_coverage.png'
    print img_folder + coverage_name
    coverage = fix_path(glob.glob(img_folder + coverage_name)[0])
    
    fti_ts_map = fix_path(glob.glob(img_folder + 'FTI_ts_map.png')[0])
    fti_ul_map = fix_path(glob.glob(img_folder + 'FTI_ul_map.png')[0])
    #ati_ub     = fix_path(glob.glob(img_folder + 'ad_ub.png')[0])
    ati_ts_map = fix_path(glob.glob(img_folder + 'ATI_ts_map.png')[0])
    ati_ul_map = fix_path(glob.glob(img_folder + 'ATI_ul_map.png')[0])
    ati_lc     = fix_path(glob.glob(img_folder + 'ATI_compositeLC.png')[0])
    
    #take the max ts and the ts_list from ati e fti ts maps
    ts_cut = kwargs['ts_cut']
    fti_ts_max, fti_ra_max, fti_dec_max, fti_ts_list, nside =\
                                    max_ts(kwargs['fti_ts_map'], ts_cut)
    ati_ts_max, ati_ra_max, ati_dec_max, ati_ts_list, nside =\
                                    max_ts(kwargs['ati_ts_map'], ts_cut)
    
    #save and show the page
    outfile = kwargs['outfile']
    if outfile is None:
        outfile = triggername + '_results.html'
    write_file(web_page.format(**locals()), outfile)
    #webbrowser.open(outfile)

if __name__ == '__main__':
    args = parser.parse_args()
    show_results(**args.__dict__)
