from fermi_gw_toolkit.pipeline import gwPipeline
import os, imp, argparse

"""Script-wide analysis settings.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument("configfile", help="Configuration file for the trigger",
                    type=str)
args = parser.parse_args()

module_name = os.path.basename(args.configfile).replace('.py', '')
config = imp.load_source(module_name, args.configfile)

IN_MAP = config.OUTMAP
TRIGGERNAME = config.TRIGGERNAME
OUTPUT_FILE_PATH = config.OUTPUT_FILE_PATH

OUTTSMAP = config.OUTTSMAP
OUTULMAP = config.OUTULMAP

"""Main pipeline object.
"""

PIPELINE = gwPipeline()

def run():
    txt_all = PIPELINE.merge_results(TRIGGERNAME, txtdir=OUTPUT_FILE_PATH)
    PIPELINE.fill_maps(in_map=IN_MAP, text_file=txt_all,
                       out_uls_map=OUTULMAP, out_ts_map=OUTTSMAP)

if __name__ == '__main__':
    run()
