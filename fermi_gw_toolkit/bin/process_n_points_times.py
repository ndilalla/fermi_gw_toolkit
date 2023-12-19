#!/usr/bin/env python

from fermi_gw_toolkit import GTBURST_PATH

import os
import argparse
import subprocess

def _ls_du(directory, message=None):
    if message is not None:
        print(message)
    cmd = 'ls -lh %s' % directory
    os.system(cmd)
    cmd = 'du -h %s' % directory
    os.system(cmd)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='process_n_points_times')

    # Intercept only --ra , --dec and --outfile
    parser.add_argument('triggername')
    parser.add_argument('--ra', required=True, type=float, nargs='+')
    parser.add_argument('--dec', required=True, type=float, nargs='+')
    parser.add_argument('--tstarts', required=True, type=float, nargs='+')
    parser.add_argument('--tstops', required=True, type=float, nargs='+')

    # This will have in args the ra, dec and outfile parameters, and in everything else a list with all the other
    # parameters

    args, everything_else = parser.parse_known_args()

    init_dir = os.getcwd()

    # Add " " to all parameters

    def add_quotes(x):

        if x.find("--") == 0:

            return x

        else:

            return "'%s'" % x

    everything_else = map(add_quotes, everything_else)

    everything_else_str = " ".join(everything_else)

    for tstarts, tstops, ra, dec in zip(args.tstarts, args.tstops, args.ra, args.dec):

        subfolder_dir = os.path.abspath("interval%s-%s" % \
                                (float(tstarts), float(tstops)))
        
        cmd_line = 'python %s/scripts/doTimeResolvedLike.py %s --ra %s '\
                   '--dec %s --tstarts %s --tstops %s ' \
                   '--outfile %s_%.3f_%.3f_res.txt --flemin 100 --flemax 1000 '\
                   '--tsmap_spec 0.5,8 --fgl_mode complete %s' %\
                   (GTBURST_PATH, args.triggername, ra, dec, tstarts, tstops, 
                    args.triggername, ra, dec, everything_else_str)
                   
        print("\nAbout to execute:\n")
        print(cmd_line)
        print("")

        try:
            subprocess.check_call(cmd_line, shell=True)
        except subprocess.CalledProcessError as err:
            print('ERROR: doTimeResolvedLike.py skipped for RA=%.3f, DEC=%.3f'%\
                (ra, dec))
            print(err)
            print(err.output)
        finally:
            _ls_du(init_dir, 'After doTimeResolved')
            if os.path.exists(subfolder_dir):
                print("Removing: %s" % subfolder_dir)
                os.system('rm -rf %s' % subfolder_dir)
                _ls_du(init_dir, 'After removal of subdir.')
