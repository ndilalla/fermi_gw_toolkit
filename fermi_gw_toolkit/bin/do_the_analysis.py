from fermi_gw_toolkit.pipeline import gwPipeline
from fermi_gw_toolkit import FERMI_GW_DATA, FERMI_GW_OUTPUT
from fermi_gw_toolkit.date_to_met import get_met
from fermi_gw_toolkit.check_file_exists import check_file_exists

import os, glob, argparse, imp, sys

"""Script-wide analysis settings.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)

parser.add_argument("configfile", help="Configuration file for the trigger",
                    type=str)
parser.add_argument('--line_number', help='Line number of the roi to analyze',
                    type=int, default=1)
parser.add_argument('--adaptive', help='Perform the adaptive time analysis',
                    type=int, required=False, default=0, choices=[0,1])
args = parser.parse_args()

module_name = os.path.basename(args.configfile).replace('.py', '')
config = imp.load_source(module_name, args.configfile)

TRIGGERNAME = config.TRIGGERNAME
DATA_PATH = config.DATA_PATH
OUTPUT_FILE_PATH = config.OUTPUT_FILE_PATH
try:
    FT2 = glob.glob(DATA_PATH +'/gll_ft2_*.fit')[0]
    print 'Found ft2 file: %s' % FT2
except:
    message = 'ft2 file not available in: %s' %DATA_PATH
    sys.exit(message)

EMIN = config.EMIN
EMAX = config.EMAX
TSMIN = config.TSMIN
IRF = config.IRF
GAL_MODEL = config.GAL_MODEL
PART_MODEL = config.PART_MODEL
UL_INDEX = config.UL_INDEX
STRATEGY = config.STRATEGY
ZMAX = config.ZMAX
THETAMAX = config.THETAMAX
ROI = config.ROI
SRC = config.SRC
N_SAMPLES = config.N_SAMPLES
BURN_IN = config.BURN_IN

if args.adaptive:
    LIST = config.OUTTIME
    KEYWORD = 'adroi'
    print 'Performing the adaptive time analysis...'
else:
    LIST = config.OUTLIST
    TSTART = float(config.TSTART)
    TSTOP = float(config.TSTOP)
    KEYWORD = 'roi'
    print 'Performing the fixed time analysis...'

"""Main pipeline object.
"""

PIPELINE = gwPipeline()

def do_the_analysis():
    with open(LIST, 'r') as roi_list:
        roi = roi_list.readlines()
        line_number = args.line_number
        if args.adaptive:
            ra, dec, tstart, tstop, deltat = roi[line_number].split()
        else:
            ra, dec = roi[line_number].split()
            tstart, tstop = TSTART, TSTOP
        print 'Selected ROI: %s, %s (line number: %d)' %(ra, dec, line_number)
        outfile = os.path.join(OUTPUT_FILE_PATH, '%s_%s_%s_%s.txt' %\
                                                (TRIGGERNAME, KEYWORD, ra, dec))
        print 'Running doTimeResolvedLike in the time interval: %s-%s' %\
                                                                (tstart, tstop)
        PIPELINE.doTimeResolvedLike(TRIGGERNAME, ra=ra, dec=dec, roi=ROI,
                            tstarts=tstart, tstops=tstop, irf=IRF,
                            galactic_model=GAL_MODEL, particle_model=PART_MODEL,
                            tsmin=TSMIN, emin=EMIN, emax=EMAX, zmax=ZMAX,
                            strategy=STRATEGY, datarepository=FERMI_GW_DATA,
                            ulphindex=UL_INDEX, outfile=outfile)
        
        subfolder_dir = os.path.abspath("interval%s-%s" %(tstart, tstop))
        try:
            xml = glob.glob(subfolder_dir + '/*filt_likeRes.xml')[0]
            expomap = glob.glob(subfolder_dir + '/*filt_expomap.fit')[0]
            new_ft1 = glob.glob(subfolder_dir + '/*filt.fit')[0]
            ltcube = glob.glob(subfolder_dir + '/*filt_ltcube.fit')[0]
            print 'Using:\n %s,\n %s,\n %s,\n %s' % (xml, expomap, new_ft1,
                                                     ltcube)
        except:
            print 'xml, expomap, ft1 or ltcube not available in: %s' %\
                                                                subfolder_dir
            return
        
        outplot = os.path.join(OUTPUT_FILE_PATH, 'corner_plot_%s_%s.png'\
                                                                    %(ra,dec))
        outul = os.path.join(OUTPUT_FILE_PATH, 'upper_limit_%s_%s' %(ra,dec))
        PIPELINE.bayesian_ul(subfolder_dir, ft1=new_ft1, ft2=FT2,
                            expomap=expomap, ltcube=ltcube, xml=xml, emin=EMIN,
                            emax=EMAX, output_file=outul, corner_plot=outplot,
                            n_samples=N_SAMPLES, src=SRC, burn_in=BURN_IN)

if __name__ == '__main__':
    do_the_analysis()
