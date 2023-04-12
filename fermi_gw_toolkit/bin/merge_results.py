#!/usr/bin/env python

__description__ = 'Merge the txt files containing doTimeResolvedLike results'

import argparse, glob, os

"""Command-line switches.
"""

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=__description__,
                                 formatter_class=formatter)

parser.add_argument("triggername", help="Trigger name", type=str)
parser.add_argument("--txtdir", help="Directory of text files", type=str,
                    required=True)
parser.add_argument("--outfile", help="Name and directory for the merged file",
                    type=str, default=None)
parser.add_argument("--keyword", help="keyword contained in txt files to merge",
                    type=str, default='roi')

def merge_results(**kwargs):
    triggername = kwargs['triggername']
    keyword = kwargs['keyword']
    if kwargs['outfile'] is None:
        outdir = kwargs['txtdir']
        out_txt_name = '%s_%s_all.txt' %(triggername, keyword)
        out_txt = os.path.join(outdir, out_txt_name)
    else:
        out_txt = kwargs['outfile']
    txtdir = '%s/%s_*_%s.txt' % (kwargs['txtdir'], triggername, keyword)
    txt_list = glob.glob(txtdir)
    print("Files to merge:\n%s" % txt_list)
    print("Preparing to merge %d text files..." %len(txt_list))
    
    print("Merging...")   
    with open(out_txt, 'w') as outfile:
        for i,txt in enumerate(txt_list):
            with open(txt) as infile:
                lines = infile.readlines()
                for line in lines:
                    if '#' in line and i>0: continue
                    outfile.write(line)
    print("Done.")
    return out_txt
    
if __name__=="__main__":
    args = parser.parse_args()
    merge_results(**args.__dict__)
