from fermi_gw_toolkit import FERMI_GW_DATA, FERMI_GW_OUTPUT
import os

"""Script-wide analysis settings.
"""

TRIGGERNAME = 'bnGW150914'

DATA_PATH = os.path.join(FERMI_GW_DATA, TRIGGERNAME)
OUTPUT_FILE_PATH = os.path.join(FERMI_GW_OUTPUT, TRIGGERNAME)

LIGO_MAP = os.path.join(DATA_PATH, 'LALInference_skymap.fits.gz,2')
FT1 = os.path.join(DATA_PATH, 'GW150914-ft1.fits')
FT2 = os.path.join(DATA_PATH, 'GW150914-ft2-1s.fits')

TSTART = 5000.  #0.
TSTOP = 8000.   #10000.
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
OUTMAP = os.path.join(OUTPUT_FILE_PATH, 'new_map.fits')
OUTCOV = os.path.join(OUTPUT_FILE_PATH, TRIGGERNAME)
OUTULMAP = os.path.join(OUTPUT_FILE_PATH, 'ul_map.fits')
OUTTSMAP = os.path.join(OUTPUT_FILE_PATH, 'ts_map.fits')
