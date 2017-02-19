from fermi_gw_toolkit.pipeline import gwPipeline
from fermi_gw_toolkit import FERMI_GW_DATA, FERMI_GW_OUTPUT
from fermi_gw_toolkit.date_to_met import get_met
import os, numpy, glob

"""Script-wide analysis settings.
"""

TRIGGERNAME = 'bnGW150914'

DATA_PATH = os.path.join(FERMI_GW_DATA, TRIGGERNAME)
OUTPUT_FILE_PATH = os.path.join(FERMI_GW_OUTPUT, TRIGGERNAME)

LIGO_MAP = os.path.join(DATA_PATH, 'LALInference_skymap.fits.gz,2')
FT1 = os.path.join(DATA_PATH, 'GW150914-ft1.fits')
FT2 = os.path.join(DATA_PATH, 'GW150914-ft2-1s.fits')
TRIGGERTIME = get_met(LIGO_MAP) #463917049

EMIN = 100.     #MeV
EMAX = 100000.  #MeV
TSMIN = 30.
IRF = 'p8_transient010e'
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
OUTTIME = os.path.join(OUTPUT_FILE_PATH, 'time_list.txt')
OUTMAP = os.path.join(OUTPUT_FILE_PATH, 'new_map.fits')
OUTCOV = os.path.join(OUTPUT_FILE_PATH, TRIGGERNAME)
OUTULMAP = os.path.join(OUTPUT_FILE_PATH, 'ul_map.fits')
OUTTSMAP = os.path.join(OUTPUT_FILE_PATH, 'ts_map.fits')

KEYWORD = 'adroi'

"""Main pipeline object.
"""

PIPELINE = gwPipeline()

def run():
    ft1, rsp, ft2, pha = PIPELINE.rawdata2package(ft1=FT1, ft2=FT2,
                            triggertime=TRIGGERTIME, triggername=TRIGGERNAME,
                            outdir=DATA_PATH)
    
    #Can we avoid to run this in order to produce the empty map?
    PIPELINE.prepare_grid(map=LIGO_MAP, out_list=OUTLIST, out_map=OUTMAP)
    
    PIPELINE.adaptive_time(in_map=LIGO_MAP, ft2=FT2, triggertime=TRIGGERTIME,
                            theta_cut=THETAMAX, zenith_cut=ZMAX, nside=32,
                            roi=0, output=OUTTIME)
    
    roi_list = open(OUTTIME, 'r')
    roi_list.readline()
    for i in range(0,2):
        ra, dec, tstart, tstop, deltat = roi_list.readline().split()
        outfile = os.path.join(OUTPUT_FILE_PATH, '%s_%s_%s_%s.txt' %\
                                                (TRIGGERNAME, KEYWORD, ra, dec))

        PIPELINE.doTimeResolvedLike(TRIGGERNAME, ra=ra, dec=dec, roi=ROI,
                            tstarts=tstart, tstops=tstop, irf=IRF,
                            galactic_model=GAL_MODEL, particle_model=PART_MODEL,
                            tsmin=TSMIN, emin=EMIN, emax=EMAX, zmax=ZMAX,
                            strategy=STRATEGY, datarepository=FERMI_GW_DATA,
                            ulphindex=UL_INDEX, outfile=outfile)

        subfolder_dir = os.path.abspath("interval%s-%s" %\
                                                (float(tstart), float(tstop)))
        xml = glob.glob(subfolder_dir + '/*filt_likeRes.xml')[0]
        expomap = glob.glob(subfolder_dir + '/*filt_expomap.fit')[0]
        new_ft1 = glob.glob(subfolder_dir + '/*filt.fit')[0]
        ltcube = glob.glob(subfolder_dir + '/*filt_ltcube.fit')[0]
        outplot = os.path.join(OUTPUT_FILE_PATH, 'corner_plot_%s_%s.png'\
                                                                    %(ra,dec))
        outul = os.path.join(OUTPUT_FILE_PATH, 'upper_limit_%s_%s' %(ra,dec))
        PIPELINE.bayesian_ul(subfolder_dir, ft1=new_ft1, ft2=ft2,
                            expomap=expomap, ltcube=ltcube, xml=xml, emin=EMIN,
                            emax=EMAX, output_file=outul, corner_plot=outplot,
                            n_samples=N_SAMPLES, src=SRC, burn_in=BURN_IN)
    roi_list.close()
    txt_all = PIPELINE.merge_results(TRIGGERNAME, txtdir=OUTPUT_FILE_PATH,
                                     keyword=KEYWORD)
    PIPELINE.fill_maps(in_map=OUTMAP, text_file=txt_all,
                       out_uls_map=OUTULMAP, out_ts_map=OUTTSMAP)

if __name__ == '__main__':
    run()
    
