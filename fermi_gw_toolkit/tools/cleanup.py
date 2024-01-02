import os
from glob import glob

from fermi_gw_toolkit import GPL_TASKROOT

# __description__= 'Tool to clean temporary files'
# formatter = argparse.ArgumentDefaultsHelpFormatter
# parser    = argparse.ArgumentParser(description=__description__,
#                                     formatter_class=formatter)
# parser.add_argument("--init", help="Rescale the MAP to NSIDE", type=int,default=None)
init = 800
end = -1
output_dir = os.path.join(GPL_TASKROOT, 'output')

good = ['bnS231229c', 'bnS231227ba', 'bnS231227ay', 'bnS231227ao', 'bnS231227am', 'bnS231227b', 'bnS231226ce', 'bnS231226bm']

for evt in good:
    print('Processing %s' % evt)
    fti_dirs = sorted(glob('%s/%s/*/FIXEDINTERVAL/' % (output_dir, evt)))
    print('Found %d FTI folders.' % len(fti_dirs))
    ati_dirs = sorted(glob('%s/%s/*/ADAPTIVEINTERVAL/' % (output_dir, evt)))
    print('Found %d ATI folders.' % len(ati_dirs))

    #print('Processing the first %d' % len(fti_dirs[init:end]))

    for fti_dir, ati_dir in zip(fti_dirs, ati_dirs):
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
    print('Done with %s' % evt)
    input()
print('Done!')