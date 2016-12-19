#!/usr/bin/env python

__description__ = 'Merge the txt files containing doTimeResolvedLike results'

import argparse, glob, os

"""Command-line switches.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument("triggername", help="Trigger name", type=str)
parser.add_argument("--txtdir", help="Directory of txt files", type=str,
                    required=True)
parser.add_argument("--outdir", help="Output directory for the merged file",
                    type=str, default=None)

def merge_results(**kwargs):
    triggername = kwargs['triggername']
    if kwargs['outdir'] is None:
        outdir = kwargs['txtdir']
    txtdir = '%s/%s_roi_*.txt' % (kwargs['txtdir'], triggername)
    txt_list = glob.glob(txtdir)
    #print "Txt-files to merge:\n%s" %txt_list
    print "Preparing to merge %d txt-files..." %len(txt_list)
    out_txt_name = '%s_all.txt' % triggername
    out_txt = os.path.join(outdir, out_txt_name)
    
    print "Merging..."
    first_txt = True
    with open(out_txt, 'w') as outfile:
        for txt in txt_list:
            with open(txt) as infile:
                if first_txt:
                    first_txt = False
                else:
                    infile.next()
                for line in infile:
                    outfile.write(line)
    print "Done."
    return out_txt
    
if __name__=="__main__":
    args = parser.parse_args()
    merge_results(**args.__dict__)
