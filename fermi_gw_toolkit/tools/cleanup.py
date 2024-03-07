import os
import argparse
from glob import glob

from fermi_gw_toolkit import GPL_TASKROOT
outfolder = os.path.join(GPL_TASKROOT, 'output')

def non_pos_int(x):
    i = int(x)
    if i > 0:
        raise ValueError('Positive values are not allowed')
    return i

def non_neg_int(x):
    i = int(x)
    if i < 0:
        raise ValueError('Negative values are not allowed')
    return i

__description__= 'Tool to clean temporary files'
formatter = argparse.ArgumentDefaultsHelpFormatter
parser    = argparse.ArgumentParser(description=__description__,
                                    formatter_class=formatter)
parser.add_argument("--init", required=True, help="Starting event [>=0]", 
                    type=non_neg_int)
parser.add_argument("--end", default=-15, help="Ending event [<=0]",
                    type=non_pos_int)
parser.add_argument("--outfolder", default=outfolder, help="Folder to clean", 
                    type=str)
args = parser.parse_args()

init = args.init
end = args.end
output_dir = args.outfolder

fti_dirs = sorted(glob('%s/*/*/FIXEDINTERVAL/' % (output_dir)))
print('Found %d FTI folders.' % len(fti_dirs))
ati_dirs = sorted(glob('%s/*/*/ADAPTIVEINTERVAL/' % (output_dir)))
print('Found %d ATI folders.' % len(ati_dirs))
lle_dirs = sorted(glob('%s/*/*/LLE/' % (output_dir)))
print('Found %d LLE folders.' % len(lle_dirs))

if end == 0:
    end = None
fti_dirs = fti_dirs[init:end]
ati_dirs = ati_dirs[init:end]
lle_dirs = lle_dirs[init:end]

print('Processing %d events' % len(fti_dirs))

for fti_dir, ati_dir, lle_dir in zip(fti_dirs, ati_dirs, lle_dirs):
    npz_files = glob('%s/*_bayesian_ul*.npz' % fti_dir)
    for npz_file in npz_files:
        os.remove(npz_file)
    print('%d npz files deleted from %s' % (len(npz_files), fti_dir))

    txt_files = glob('%s/*_res.txt' % fti_dir)
    for txt_file in txt_files:
        os.remove(txt_file)
    print('%d res txt files deleted from %s' % (len(txt_files), fti_dir))

    png_files = glob('%s/*_corner_plot.png' % fti_dir)
    for png_file in png_files:
        os.remove(png_file)
    print('%d png files deleted from %s' % (len(png_files), fti_dir))

    txt_files = glob('%s/*_res.txt' % ati_dir)
    for txt_file in txt_files:
        os.remove(txt_file)
    print('%d res txt files deleted from %s' % (len(txt_files), ati_dir))

    txt_files = glob('%s/*_res.txt' % lle_dir)
    for txt_file in txt_files:
        os.remove(txt_file)
    print('%d res txt files deleted from %s' % (len(txt_files), lle_dir))

    #input()
print('Done!')
