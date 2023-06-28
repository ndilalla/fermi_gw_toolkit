import os
from glob import glob

from fermi_gw_toolkit import GPL_TASKROOT

output_dir = os.path.join(GPL_TASKROOT, 'output')
fti_dirs = sorted(glob('%s/*/*/FIXEDINTERVAL/' % (output_dir)))
print('Found %d folders.' % len(fti_dirs))
print('Processing the first %d' % len(fti_dirs[:-10]))

for fti_dir in fti_dirs[:-10]:
    npz_files = glob('%s/*_bayesian_ul*.npz' % fti_dir)
    for npz_file in npz_files:
        cmd = 'rm %s' % npz_file
        print(cmd)
        #os.system(cmd)
    print('%d files deleted from %s' % (len(npz_files), fti_dir))
    input()
    