from fermi_gw_toolkit.pipeline import gwPipeline
from fermi_gw_toolkit.date_to_met import get_met
from fermi_gw_toolkit.check_file_exists import check_file_exists
import os, argparse, imp

"""Script-wide analysis settings.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)

parser.add_argument("configfile", help="Configuration file for the trigger",
                    type=str)
args = parser.parse_args()

module_name = os.path.basename(args.configfile).replace('.py', '')
config = imp.load_source(module_name, args.configfile)

TRIGGERNAME = config.TRIGGERNAME
DATA_PATH = config.DATA_PATH
LIGO_MAP = config.LIGO_MAP
TRIGGERTIME = get_met(LIGO_MAP)

download = False
try:
    FT1 = check_file_exists(config.FT1)
    FT2 = check_file_exists(config.FT2)
except:
    print "No FT1 or FT2 found."
    download = True

TSTART = config.TSTART
TSTOP = config.TSTOP
EMIN = config.EMIN
EMAX = config.EMAX
IRF = config.IRF
ZMAX = config.ZMAX
THETAMAX = config.THETAMAX

OUTTIME = config.OUTTIME
OUTLIST = config.OUTLIST
OUTMAP = config.OUTMAP
OUTCOV = config.OUTCOV

"""Main pipeline object.
"""

PIPELINE = gwPipeline()

def prepare_for_analysis():
    if download:
        _FT1, _FT2 = PIPELINE.download_LAT_data(TRIGGERNAME, emin=EMIN,
                            emax=EMAX, outdir=DATA_PATH, irf=IRF,
                            tstart=TRIGGERTIME-1000, tstop=TRIGGERTIME+10000)
    else:
        _FT1, _FT2 = FT1, FT2
    
    ft1, rsp, ft2, pha = PIPELINE.rawdata2package(ft1=_FT1, ft2=_FT2,
                            triggertime=TRIGGERTIME, triggername=TRIGGERNAME,
                            outdir=DATA_PATH)
    
    PIPELINE.get_coverage(in_map=LIGO_MAP, ft2=ft2, start_time=TRIGGERTIME,
                            stop_time=TRIGGERTIME+10000., theta_cut=THETAMAX,
                            zenith_cut=ZMAX, outroot=OUTCOV)
        
    PIPELINE.adaptive_time(in_map=LIGO_MAP, ft2=ft2, triggertime=TRIGGERTIME,
                            theta_cut=THETAMAX, zenith_cut=ZMAX, nside=32,
                            roi=0, output=OUTTIME)
    
    PIPELINE.prepare_grid(map=LIGO_MAP, out_list=OUTLIST, out_map=OUTMAP)

if __name__ == '__main__':
    prepare_for_analysis()
