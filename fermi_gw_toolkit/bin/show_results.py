#!/usr/bin/env python
import os, glob, argparse
import shutil
import numpy
import healpy as hp
#import webbrowser
import astropy.io.fits as pyfits
from fermi_gw_toolkit import GPL_TASKROOT#, DECORATOR_PATH
from fermi_gw_toolkit.lib.contour_finder import pix_to_sky
from fermi_gw_toolkit.lib.local_database import gw_local_database
from fermi_gw_toolkit.lib.check_association import check_catalog, check_sun_moon
from fermi_gw_toolkit.lib.html_lib import *

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)

_db_file = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4b_events.json')
def fix_path(local_path):
    #return local_path.replace(GPL_TASKROOT, DECORATOR_PATH)
    return local_path

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
    radius = hp.nside2resol(nside, arcmin=True) / 60. #deg
    ts_max = str(round(numpy.nanmax(ts_map), 1))
    px_max = numpy.nanargmax(ts_map)
    ra_max, dec_max = pix_to_sky(px_max,nside)
    # hp.pix2ang(nside, px_max, lonlat=True)
    ra_max = round(ra_max, 2)
    dec_max = round(dec_max, 2)
    ts_list = insert_ts_list(ts_map, ts_cut, nside, text, radius)
    return ts_max, ra_max, dec_max, ts_list, nside, radius

def insert_ts_list(ts_map, ts_cut, nside, text, radius):
    ts_px = numpy.argwhere(ts_map>ts_cut)
    #sort ts descending
    idx = numpy.argsort(-ts_map[ts_px], axis=0)
    ts_px = numpy.take_along_axis(ts_px, idx, axis=0).flatten()
    table = ""
    for px in ts_px[1:]:
        ts = str(round(ts_map[px],1))
        ra, dec = pix_to_sky(px, nside)
        src_names, src_sep = check_catalog(ra, dec, radius)
        #ra, dec = hp.pix2ang(nside, px, lonlat=True)
        ra = round(ra, 2)
        dec = round(dec, 2)
        table += open_tbody
        table += list_content.format(text, ts, ra, dec)
        table += insert_src_list(src_names, src_sep)
        table += end_tbody
    return table

def insert_src_list(src_names, src_sep):
    table = ""
    for name, sep in zip(src_names, src_sep):
        _sep = str(round(sep, 2))
        table += src_content.format(name, _sep)
    return table

def min_max_ul(map_path):
    ul_map, header = hp.read_map(map_path, h=True)
    ul_max = round(numpy.nanmax(ul_map[numpy.nonzero(ul_map)]) / 1e-9, 1)
    ul_min = round(numpy.nanmin(ul_map[numpy.nonzero(ul_map)]) / 1e-10, 2)
    return ul_min, ul_max

def proc_ts_count_maps(file_list, met, radius=1, cp_folder=None):
    if len(file_list) == 0:
        print('TS and count maps not found in file list %s' % file_list)
        return ''
    ts_count_map = ''
    for file_coords in file_list:
        with open(file_coords, 'r') as f:
            f.readline()
            pgw_ra_max, pgw_dec_max, pgw_ts_max = f.readline().split()
        pgw_ra_max = round(float(pgw_ra_max), 2)
        pgw_dec_max = round(float(pgw_dec_max), 2)
        pgw_ts_max = round(float(pgw_ts_max), 1)
        pgw_src_names, pgw_src_sep = check_catalog(pgw_ra_max, pgw_dec_max, 
                                                   radius)
        pgw_n_src = len(pgw_src_names)
        pgw_max_src_list = insert_src_list(pgw_src_names, pgw_src_sep)
        pgw_sun, pgw_moon = check_sun_moon(pgw_ra_max, pgw_dec_max, met, radius)
        pgw_ts_map = fix_path(file_coords.replace('_coords.txt', '_tsmap.png'))
        pgw_c_map = fix_path(pgw_ts_map.replace('_tsmap', '_cmap'))
        if cp_folder is not None:
            shutil.copy(pgw_ts_map, cp_folder)
            shutil.copy(pgw_c_map, cp_folder)
        ts_count_map += ts_count_map_content.format(**locals())
    return ts_count_map

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
    covmax = round(cov[index] * 100, 2)
    return cov0, t0, ssa, tmax, covmax
    
def show_results(**kwargs):
    web_page = load_file(kwargs['template'])
    styles = kwargs['styles']
    
    #define all the variables to be used in the template
    triggername = kwargs['triggername'].replace('bn','')
    triggertime = round(kwargs['triggertime'], 2)
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

    #FTI
    #take the max ts and the ts_list from fti ts maps
    ts_cut = kwargs['ts_cut'] 
    fti_ts_max, fti_ra_max, fti_dec_max, fti_ts_list, nside, radius =\
                                    max_ts(kwargs['fti_ts_map'], ts_cut)
    # check the catalog and if Sun and Moon are close to the pixel
    fti_src_names, fti_src_sep = check_catalog(fti_ra_max, fti_dec_max, radius)
    fti_n_src = len(fti_src_names)
    fti_max_src_list = insert_src_list(fti_src_names, fti_src_sep)
    _met = triggertime + 0.5 * (tstop - tstart)
    fti_sun, fti_moon = check_sun_moon(fti_ra_max, fti_dec_max, _met, radius)
    
    #take the max/min UL from fti ul maps
    outdir = os.path.dirname(kwargs['fti_ts_map'])
    fti_ = proc_ts_count_maps(glob.glob(outdir + '/FIXEDINTERVAL/%s_*_coords.txt' % kwargs['triggername']), _met, cp_folder=img_folder)
    
    # ATI
    #take the max ts and the ts_list from ati ts maps
    ati_ts_max, ati_ra_max, ati_dec_max, ati_ts_list, nside, radius =\
                                    max_ts(kwargs['ati_ts_map'], ts_cut)
    # check the catalog and if Sun and Moon are close to the pixel
    ati_src_names, ati_src_sep = check_catalog(ati_ra_max, ati_dec_max, radius)
    ati_n_src = len(ati_src_names)
    ati_max_src_list = insert_src_list(ati_src_names, ati_src_sep)
    ati_sun, ati_moon = check_sun_moon(ati_ra_max, ati_dec_max, _met, radius)

    #take the max/min UL from ati ul maps
    fti_ul_path = os.path.join(outdir, 'FTI_ul_map.fits')
    fti_ul_min, fti_ul_max = min_max_ul(fti_ul_path)
    ati_ul_path = os.path.join(outdir, 'ATI_ul_map.fits')
    ati_ul_min, ati_ul_max = min_max_ul(ati_ul_path)
    
    #LLE
    sigma_cut = 4
    lle_ = ''
    lle_link = ''
    if lle_ts_map is not None: 
        lle_ts_max, lle_ra_max, lle_dec_max, lle_ts_list, lle_nside, radius =\
                                max_ts(kwargs['lle_ts_map'], sigma_cut, 'SIGMA')
        lle_src_names, lle_src_sep = check_catalog(lle_ra_max, lle_dec_max, radius)
        lle_n_src = len(lle_src_names)
        lle_max_src_list = insert_src_list(lle_src_names, lle_src_sep)
        lle_sun, lle_moon = check_sun_moon(lle_ra_max, lle_dec_max, _met,
                                           radius)
        lle_ = lle_content.format(**locals())
        lle_link = lle_link_content
    
    #PGWAVE
    pgwave_ = proc_ts_count_maps(glob.glob(outdir + '/PGWAVE/%s_*_coords.txt' %\
                                   kwargs['triggername']), _met, 
                                   cp_folder=img_folder)

    #process the coverage file to recover some useful info to display
    cov_file_path = os.path.join(outdir, 'bn%s_coverage.npz' % triggername)
    cov0, t0, ssa, tmax, covmax = proc_coverage(cov_file_path)
    
    #load the events database and add the relevant info
    db_file = kwargs['db_file']
    db = gw_local_database.load(db_file)
    event_dict = {'Date'   : date,
                  'Time'   : time,
                  'Fti_ts' : fti_ts_max,
                  'Ati_ts' : ati_ts_max,
                  'Cov_0'  : cov0,
                  'SSA'    : ssa,
                  'Cov_max': covmax}
    version = img_folder.split('/')[-3]
    db.update(kwargs['triggername'], version, event_dict)
    db.save(db_file)
    
    #take Bayesian UL from database (if available)
    ene_ul = db.get_value(kwargs['triggername'], version, 'Ene_ul')
    if ene_ul is not None:
        ph_ul = db.get_value(kwargs['triggername'], version, 'Ph_ul')
        cl = int(db.get_value(kwargs['triggername'], version, 'CL') * 100)
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
