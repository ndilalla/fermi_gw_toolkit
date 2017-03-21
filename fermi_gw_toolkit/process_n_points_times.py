#!/usr/bin/env python

import argparse
import subprocess

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

    # Add " " to all parameters

    def add_quotes(x):

        if x.find("--") == 0:

            return x

        else:

            return "'%s'" % x

    everything_else = map(add_quotes, everything_else)

    everything_else_str = " ".join(everything_else)

    for tstarts, tstops, ra, dec in zip(args.tstarts, args.tstops, args.ra, args.dec):

        cmd_line = 'doTimeResolvedLike.py %s --ra %s --dec %s ' \
                   '--tstarts %s --tstops %s ' \
                   '--outfile %s_%.3f_%.3f_res.txt %s' % (args.triggername, ra, dec, tstarts, tstops,  args.triggername, ra, dec,
                                                          everything_else_str)

        print("\nAbout to execute:\n")
        print cmd_line
        print("")

        subprocess.check_call(cmd_line, shell=True)

