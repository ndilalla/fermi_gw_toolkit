#!/usr/bin/env python
import os, glob, argparse
import numpy
import healpy as hp
#import webbrowser
import astropy.io.fits as pyfits
from fermi_gw_toolkit.lib.contour_finder import pix_to_sky
from fermi_gw_toolkit.lib.local_database import gw_local_database
from fermi_gw_toolkit.lib.html_lib import *

#from automatic_pipeline.utils import send_email

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)

_nfs_home='/nfs/farm/g/glast/u26/GWPIPELINE'
_db_file = os.path.join(_nfs_home, 'output', 'db_gw_events.pkl')
def fix_path(local_path):
    _html_home='http://glast-ground.slac.stanford.edu/Decorator/exp/Fermi/Decorate/groups/grb/GWPIPELINE/'
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
parser.add_argument("--lle_ts_map", help="LLE TS map path", type=str,
                    required=True)
parser.add_argument("--img_folder", help="Image folder", type=str,
                    required=False, default=".")
parser.add_argument("--template", help="Template", type=str, required=False,
                    default='results_template.html')
parser.add_argument("--styles", help="Css file for style", type=str,
                    required=False, default='styles.css')
parser.add_argument("--db_file", help="File used for database", type=str,
                    required=False, default=_db_file)

def get_date(ligo_map):
    hdulist = pyfits.open(ligo_map)
    date_obs = hdulist[1].header['DATE-OBS']
    return date_obs[:10], date_obs[11:19]

def load_file(file_path):
    with open(file_path, 'r') as f: 
        page = f.read()
    return page

def write_file(text, outfile):
    with open(outfile, "w") as output:
        output.write(text)
    
def max_ts(map_path, ts_cut, text='TS'):
    if not os.path.exists(map_path):
        return 0, 0, 0, "", 0
    ts_map, header = hp.read_map(map_path, h=True)
    header = dict(header)
    nside = header['NSIDE']
    ts_max = round(numpy.nanmax(ts_map),2)
    px_max = numpy.nanargmax(ts_map)
    ra_max, dec_max = pix_to_sky(px_max,nside)
    # hp.pix2ang(nside, px_max, lonlat=True)
    ra_max = round(ra_max, 2)
    dec_max = round(dec_max, 2)
    ts_list = insert_ts_list(ts_map, ts_cut, nside, text)
    return ts_max, ra_max, dec_max, ts_list, nside

def insert_ts_list(ts_map, ts_cut, nside, text):
    ts_px = numpy.argwhere(ts_map>ts_cut)
    table = ""
    for px in ts_px.T[0]:
        ts = round(ts_map[px],2)
        ra, dec = pix_to_sky(px,nside)
        #ra, dec = hp.pix2ang(nside, px, lonlat=True)
        ra = round(ra, 2)
        dec = round(dec, 2)
        table += list_content.format(text, ts, ra, dec)
    return table

def min_max_ul(map_path):
    ul_map, header = hp.read_map(map_path, h=True)
    ul_max = round(numpy.nanmax(ul_map[numpy.nonzero(ul_map)]) / 1e-9, 1)
    ul_min = round(numpy.nanmin(ul_map[numpy.nonzero(ul_map)]) / 1e-10, 2)
    return ul_min, ul_max

def proc_pgwave(file_list):
    if len(file_list) == 0:
        print('PGWAVE map not found.')
        return ''
    pgwave = ''
    for file_coords in file_list:
        with open(file_coords, 'r') as f:
            f.readline()
            ra_max, dec_max, ts_max = f.readline().split()
        ra_max = round(float(ra_max), 2)
        dec_max = round(float(dec_max), 2)
        ts_max = round(float(ts_max), 2)
        ts_map = fix_path(file_coords.replace('_coords.txt', '_tsmap.png'))
        c_map = fix_path(ts_map.replace('_tsmap', '_cmap'))
        pgwave += pgw_content.format(**locals())
    return pgwave

def proc_coverage(cov_path):
    npzfile = numpy.load(cov_path)
    dt = npzfile['dt']
    cov = npzfile['cov']
    cov0 = round(cov[0]*100, 1)
    t0 = round(dt[0], 1)
    ssa = False
    if t0 > 0.01:
        ssa = True
        t0 = '(%s ks)' % t0
    else:
        t0 = ''
    index = numpy.argmax(cov)
    tmax = round(dt[index], 1)
    covmax = round(cov[index]*100, 2)
    return cov0, t0, ssa, tmax, covmax
    
def show_results(**kwargs):
    web_page = load_file(kwargs['template'])
    #styles = load_file(kwargs['styles'])
    
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
    coverage_name = '/bn' + triggername +'_prob_coverage.png'
    coverage = fix_path(glob.glob(img_folder + coverage_name)[0])
    fti_ts_map = fix_path(glob.glob(img_folder + '/FTI_ts_map.png')[0])
    fti_ul_map = fix_path(glob.glob(img_folder + '/FTI_ul_map.png')[0])
    #ati_ub     = fix_path(glob.glob(img_folder + 'ad_ub.png')[0])
    ati_ts_map = fix_path(glob.glob(img_folder + '/ATI_ts_map.png')[0])
    ati_ul_map = fix_path(glob.glob(img_folder + '/ATI_ul_map.png')[0])
    ati_lc = fix_path(glob.glob(img_folder + '/ATI_compositeLC.png')[0])
    pgw_cmap = fix_path(glob.glob(img_folder + '/PGW_countmap.png')[0])
    try:
        lle_ts_map = fix_path(glob.glob(img_folder + '/LLE_ts_map.png')[0])
    except IndexError:
        lle_ts_map = None
        print('LLE map not found.')

    #take the max ts and the ts_list from ati e fti ts maps
    ts_cut = kwargs['ts_cut']
    sigma_cut = 4
    fti_ts_max, fti_ra_max, fti_dec_max, fti_ts_list, nside =\
                                    max_ts(kwargs['fti_ts_map'], ts_cut)
    ati_ts_max, ati_ra_max, ati_dec_max, ati_ts_list, nside =\
                                    max_ts(kwargs['ati_ts_map'], ts_cut)
    
    #take the max/min UL from ati e fti ul maps
    outdir = os.path.dirname(kwargs['fti_ts_map'])
    fti_ul_path = os.path.join(outdir, 'FTI_ul_map.fits')
    fti_ul_min, fti_ul_max = min_max_ul(fti_ul_path)
    ati_ul_path = os.path.join(outdir, 'ATI_ul_map.fits')
    ati_ul_min, ati_ul_max = min_max_ul(ati_ul_path)
    
    #LLE
    lle = ''
    if lle_ts_map is not None: 
        lle_ts_max, lle_ra_max, lle_dec_max, lle_ts_list, nside =\
                                    max_ts(kwargs['lle_ts_map'], sigma_cut, 
                                    'SIGMA')
        lle = lle_content.format(**locals())
    
    #PGWAVE
    pgwave = proc_pgwave(glob.glob(outdir + '/PGWAVE/%s_*_coords.txt' %\
                                   kwargs['triggername']))

    #process the coverage file to recover some useful info to display
    cov_file_path = os.path.join(outdir, 'bn%s_coverage.npz' % triggername)
    cov0, t0, ssa, tmax, covmax = proc_coverage(cov_file_path)
    
    #load the events database and add the relevant info
    db_file = kwargs['db_file']
    db = gw_local_database.load(db_file)
    event_dict = {'Date'   : date,
                  'Time'   : time,
                  'Fti_ts' : fti_ts_max,
                  'Ati_ts' : ati_ts_max}
    version = img_folder.split('/')[-3]
    db.update(kwargs['triggername'], version, event_dict)
    db.save(db_file)
    
    #take Bayesian UL from database (if available)
    ph_ul = db.get(kwargs['triggername'], version, 'Ph_ul')
    ene_ul = db.get(kwargs['triggername'], version, 'Ene_ul')
    if ene_ul is not None:
        cl = int(db.get(kwargs['triggername'], version, 'CL') * 100)
        ph_ul = round(ph_ul / 1e-7, 2)
        ene_ul = round(ene_ul / 1e-10, 2)
        bayesian_ul = bayesian_ul_content.format(**locals())
    else:
        bayesian_ul = ''
        print('Bayesian UL not found.')
    
    #save and show the page
    outfile = kwargs['outfile']
    if outfile is None:
        outfile = triggername + '_results.html'
    write_file(web_page.format(**locals()), outfile)

    return outfile
    #webbrowser.open(outfile)

if __name__ == '__main__':

    args = parser.parse_args()
    outfile = show_results(**args.__dict__)

    text = """ Results here: %s  """ % outfile

    #send_email('nicola.omodei@gmail.com', 'Processing of %s completed' % args.triggername, text)
