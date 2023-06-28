import os
from glob import glob

from fermi_gw_toolkit import GPL_TASKROOT

output_dir = os.path.join(GPL_TASKROOT, 'output')
fti_dirs = sorted(glob('%s/*/*/FIXEDINTERVAL/' % (output_dir)))

for fti_dir in fti_dirs:
    npz_files = glob('%s/*_bayesian_ul*.npz' % fti_dir)
    print(npz_files)



