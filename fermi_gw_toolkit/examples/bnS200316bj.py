from fermi_gw_toolkit.pipeline import gwPipeline
from fermi_gw_toolkit import FERMI_GW_DATA, FERMI_GW_OUTPUT
from fermi_gw_toolkit.utils.date_to_met import get_met
import os, numpy, glob, shutil

"""Script-wide analysis settings.
"""

TRIGGERNAME = 'bnS200316bj'
VERSION = 'v05'

DATA_PATH = os.path.join(FERMI_GW_DATA, TRIGGERNAME)
OUTPUT_FILE_PATH = os.path.join(FERMI_GW_OUTPUT, TRIGGERNAME)
try:
    os.mkdir(OUTPUT_FILE_PATH)
except FileExistsError:
    pass

LIGO_MAP = os.path.join(DATA_PATH, VERSION, 'HEALPIX.fits')
FT1 = os.path.join(DATA_PATH, VERSION, 'FT1.fits')
FT2 = os.path.join(DATA_PATH, VERSION, 'FT2.fits')
TRIGGERTIME = get_met(LIGO_MAP)

TSTART = 0. #0
TSTOP = 5000.  #10000.
EMIN = 100.     #MeV
EMAX = 100000.  #MeV
TSMIN = 30.
IRF = 'p8_source'
GAL_MODEL = 'template'
PART_MODEL = 'isotr template'
UL_INDEX = -2.
STRATEGY = 'time'
ZMAX = 100.
THETAMAX = 65.
ROI = 8.0
SRC = 'GRB'
N_SAMPLES = 500
BURN_IN = 200

OUTLIST = os.path.join(OUTPUT_FILE_PATH, 'roi_list.txt')
OUTMAP = os.path.join(OUTPUT_FILE_PATH, 'new_map.fits')
OUTCOV = os.path.join(OUTPUT_FILE_PATH, TRIGGERNAME)
OUTULMAP = os.path.join(OUTPUT_FILE_PATH, 'FTI_ul_map.fits')
OUTTSMAP = os.path.join(OUTPUT_FILE_PATH, 'FTI_ts_map.fits')

KEYWORD = 'res'

"""Main pipeline object.
"""

PIPELINE = gwPipeline()

def run():
    ft1, rsp, ft2, pha = PIPELINE.rawdata2package(ft1=FT1, ft2=FT2,
                            triggertime=TRIGGERTIME, triggername=TRIGGERNAME,
                            outdir=DATA_PATH)

    PIPELINE.get_coverage(in_map=LIGO_MAP, ft2=ft2, start_time=TRIGGERTIME,
                            stop_time=TRIGGERTIME+10000., theta_cut=THETAMAX,
                            zenith_cut=ZMAX, outroot=OUTCOV)

    PIPELINE.prepare_grid(map=LIGO_MAP, out_list=OUTLIST, out_map=OUTMAP)

    roi_list = open(OUTLIST, 'r')
    roi_list.readline()
    for i in range(0,2):
        ra, dec = roi_list.readline().split()
        ra, dec = float(ra), float(dec)
        outfile = os.path.join(OUTPUT_FILE_PATH, '%s_%.3f_%.3f_%s.txt' %\
                                                (TRIGGERNAME, ra, dec, KEYWORD))
        
        subfolder_dir, xml, expomap, new_ft1, ltcube =\
            PIPELINE.doTimeResolvedLike(TRIGGERNAME, ra=ra, dec=dec, roi=ROI,
                            tstarts=TSTART, tstops=TSTOP, irf=IRF,
                            galactic_model=GAL_MODEL, particle_model=PART_MODEL,
                            tsmin=TSMIN, emin=EMIN, emax=EMAX, zmax=ZMAX,
                            strategy=STRATEGY, datarepository=FERMI_GW_DATA,
                            ulphindex=UL_INDEX, outfile=outfile)
        outplot = os.path.join(OUTPUT_FILE_PATH, '%s_%.3f_%.3f_%s.png' %\
                                    (TRIGGERNAME, ra, dec, 'corner_plot'))
        outul = os.path.join(OUTPUT_FILE_PATH, '%s_%.3f_%.3f_%s' %\
                                    (TRIGGERNAME, ra, dec, 'bayesian_ul'))
        PIPELINE.bayesian_ul(subfolder_dir, ft1=new_ft1, ft2=ft2,
                            expomap=expomap, ltcube=ltcube, xml=xml, emin=EMIN,
                            emax=EMAX, output_file=outul, corner_plot=outplot,
                            n_samples=N_SAMPLES, src=SRC, burn_in=BURN_IN)
        
        if os.path.exists(subfolder_dir):
            print('Removing the folder %s' % subfolder_dir)
            shutil.rmtree(subfolder_dir)
        
    roi_list.close()
    txt_all = PIPELINE.merge_results(TRIGGERNAME, txtdir=OUTPUT_FILE_PATH,
                                     keyword=KEYWORD)
    PIPELINE.fill_maps(in_map=OUTMAP, text_file=txt_all,
                       out_uls_map=OUTULMAP, out_ts_map=OUTTSMAP)

if __name__ == '__main__':
    run()
