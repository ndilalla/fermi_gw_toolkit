#!/usr/bin/env python

import argparse
import subprocess
import os
import glob

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='process_n_points')

    # args for doTimeResolvedLike
    parser.add_argument('triggername')
    parser.add_argument('--ra', required=True, type=float, nargs='+')
    parser.add_argument('--dec', required=True, type=float, nargs='+')
    parser.add_argument('--roi', type=float, required=True)
    parser.add_argument('--tstarts', type=str, required=True)
    parser.add_argument('--tstops', type=str, required=True)
    parser.add_argument('--zmax', type=float, required=True)
    parser.add_argument('--emin', type=float, required=True)
    parser.add_argument('--emax', type=float, required=True)
    parser.add_argument('--irf', type=str, required=True)
    parser.add_argument('--galactic_model', type=str, required=True)
    parser.add_argument('--particle_model', type=str, required=True)
    parser.add_argument('--tsmin', type=float, required=True)
    parser.add_argument('--strategy', type=str, required=True)
    parser.add_argument('--thetamax', type=float, required=True)
    parser.add_argument('--datarepository', type=str, required=True)
    parser.add_argument('--ulphindex', type=float, required=True)

    # args for bayesian_ul
    parser.add_argument('--bayesian_ul', type=int, required=True, choices=[0, 1])
    parser.add_argument('--ft2', type=str, required=True)
    parser.add_argument('--src', type=str, required=True)
    parser.add_argument('--burn_in', type=int, required=True)
    parser.add_argument('--n_samples', type=int, required=True)

    # Add " " to all parameters
    # def add_quotes(x):
    #    if x.find("--") == 0:
    #        return x
    #    else:
    #        return "'%s'" % x

    # everything_else = map(add_quotes, everything_else)
    # everything_else_str = " ".join(everything_else)

    args = parser.parse_args()

    for ra, dec in zip(args.ra, args.dec):
        outfile = '%s_%.3f_%.3f_res.txt' % (args.triggername, ra, dec)
        # cmd_line = 'python $FERMI_DIR/lib/python/GtBurst/scripts/'
        cmd_line = 'doTimeResolvedLike.py %s --ra %s --dec %s --outfile %s ' \
                   '--roi %s --tstarts %s --tstops %s --zmax %s --emin %s ' \
                   '--emax %s --irf %s --galactic_model %s ' \
                   '--particle_model "%s" --tsmin %s --strategy %s ' \
                   '--thetamax %s --datarepository %s --ulphindex %s --flemin 100 --flemax 1000 ' \
                   '--tsmap_spec 0.5,8 --fgl_mode complete' % \
                   (args.triggername, ra, dec, outfile,
                    args.roi, args.tstarts, args.tstops, args.zmax, args.emin,
                    args.emax, args.irf, args.galactic_model,
                    args.particle_model, args.tsmin, args.strategy,
                    args.thetamax, args.datarepository, args.ulphindex)

        print("\nAbout to execute:\n")
        print cmd_line
        print("")

        subprocess.check_call(cmd_line, shell=True)

        if args.bayesian_ul is 0:
            print('Bayesian UL not executed.')
            continue

        init_dir = os.getcwd()
        subfolder_dir = os.path.abspath("interval%s-%s" % \
                                        (float(args.tstarts), float(args.tstops)))
        xml = glob.glob(subfolder_dir + '/*filt_likeRes.xml')[0]
        expomap = glob.glob(subfolder_dir + '/*filt_expomap.fit')[0]
        new_ft1 = glob.glob(subfolder_dir + '/*filt.fit')[0]
        ltcube = glob.glob(subfolder_dir + '/*filt_ltcube.fit')[0]
        print 'Using:\n %s,\n %s,\n %s,\n %s' % (xml, expomap, new_ft1,
                                                 ltcube)
        outplot = os.path.join(init_dir, '%s_%.3f_%.3f_corner_plot.png' % \
                               (args.triggername, ra, dec))
        outul = os.path.join(init_dir, '%s_%.3f_%.3f_bayesian_ul' % \
                             (args.triggername, ra, dec))
        print("")
        print "Changing working directory to: %s" % subfolder_dir
        os.chdir(subfolder_dir)
        cmd_line = 'python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/bayesian_ul.py ' \
                   '--ft1 %s --ft2 %s --expomap %s --ltcube %s --xml %s ' \
                   '--emin %s --emax %s --output_file %s --corner_plot %s ' \
                   '--n_samples %s --src %s --burn_in %s' % \
                   (new_ft1, args.ft2, expomap, ltcube, xml, args.emin,
                    args.emax, outul, outplot, args.n_samples, args.src,
                    args.burn_in)

        print("\nAbout to execute:\n")
        print cmd_line
        print("")

        subprocess.check_call(cmd_line, shell=True)

        print "Returning to: %s" % init_dir
        os.chdir(init_dir)
