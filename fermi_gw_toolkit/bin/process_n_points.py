#!/usr/bin/env python

import argparse
import subprocess
import os
import glob
from fermi_gw_toolkit import GTBURST_PATH, FERMI_GW_ROOT
from fermi_gw_toolkit.utils.get_sources import getSourcesInTheROI
from GtBurst.commands import fits2png
from GtBurst.commands.gtdotsmap import thisCommand as gtdotsmap

def _execute_command(cmd_line):

    print("\nAbout to execute:\n")
    print(cmd_line)
    print("")

    subprocess.check_output(cmd_line, stderr=subprocess.STDOUT, shell=True)

def _chdir_rmdir(init_dir, subfolder_dir):
    print("Returning to: %s" % init_dir)
    os.chdir(init_dir)
    print("Removing: %s" % subfolder_dir)
    os.system('rm -rf %s' % subfolder_dir)

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
    
    # args for ts map
    parser.add_argument('--do_tsmap', type=int, required=False, choices=[0, 1], default=0)

    # args for simulation
    parser.add_argument('--sim_ft1_tar', help="Path to .tar file containing simulated FT1 data (full sky)", type=str,
                        required=False, default=None)

    # Add " " to all parameters
    # def add_quotes(x):
    #    if x.find("--") == 0:
    #        return x
    #    else:
    #        return "'%s'" % x

    # everything_else = map(add_quotes, everything_else)
    # everything_else_str = " ".join(everything_else)

    args = parser.parse_args()

    # Get absolute path of FT2
    ft2 = os.path.abspath(os.path.expandvars(args.ft2))

    assert os.path.exists(ft2), "FT2 %s does not exist" % ft2

    tsmap_spec = "0.5,8"
    if args.bayesian_ul == 0 or args.do_tsmap == 1:
        fgl_mode = 'complete'
    else:
        fgl_mode = 'fast'

    for ra, dec in zip(args.ra, args.dec):

        outfile = '%s_%.3f_%.3f_res.txt' % (args.triggername, ra, dec)
        cmd_line = 'python %s/scripts/doTimeResolvedLike.py %s --ra %s '\
                   '--dec %s --outfile %s --roi %s --tstarts %s ' \
                   '--tstops %s --zmax %s --emin %s --emax %s --irf %s '\
                   '--galactic_model %s --particle_model "%s" --tsmin %s '\
                   '--strategy %s --thetamax %s --datarepository %s '\
                   '--ulphindex %s --flemin 100 --flemax 1000 ' \
                   '--tsmap_spec %s --fgl_mode %s' % \
                   (GTBURST_PATH, args.triggername, ra, dec, outfile,
                    args.roi, args.tstarts, args.tstops, args.zmax, args.emin,
                    args.emax, args.irf, args.galactic_model,
                    args.particle_model, args.tsmin, args.strategy,
                    args.thetamax, args.datarepository, args.ulphindex, 
                    tsmap_spec, fgl_mode)

        try:
            pass
            _execute_command(cmd_line)
        except subprocess.CalledProcessError as err:
            print('ERROR: doTimeResolvedLike.py skipped for RA=%.3f, DEC=%.3f'%\
                (ra, dec))
            print(err)
            print(err.output)
            # if "ModuleNotFoundError" in err.output:
            #     raise RuntimeError
            # else:
            #     continue
            continue

        # Figure out path of output files for the Bayesian upper limit and/or the simulation step below
        init_dir = os.getcwd()
        subfolder_dir = os.path.abspath("interval%s-%s" % \
                                        (float(args.tstarts), float(args.tstops)))
        try:
            xml = glob.glob(subfolder_dir + '/*filt_likeRes.xml')[0]
            expomap = glob.glob(subfolder_dir + '/*filt_expomap.fit')[0]
            new_ft1 = glob.glob(subfolder_dir + '/*filt.fit')[0]
            ltcube = glob.glob(subfolder_dir + '/*filt_ltcube.fit')[0]
        except IndexError:
            print('Data are not available for pixel at RA=%.3f, DEC=%.3f' %\
                (ra, dec))
            print('Skipping this one...')
            #_chdir_rmdir(init_dir, subfolder_dir)
            continue

        if args.bayesian_ul == 0 or args.do_tsmap == 1:
            print('Bayesian UL not executed.')
        else:

            print('Using:\n %s,\n %s,\n %s,\n %s' % (xml, expomap, new_ft1,
                                                     ltcube))
            outplot = os.path.join(init_dir, '%s_%.3f_%.3f_corner_plot.png' % \
                                   (args.triggername, ra, dec))
            outul = os.path.join(init_dir, '%s_%.3f_%.3f_bayesian_ul' % \
                                 (args.triggername, ra, dec))
            print("")
            print("Changing working directory to: %s" % subfolder_dir)
            os.chdir(subfolder_dir)
            cmd_line = 'python %s/bin/bayesian_ul.py --ft1 %s --ft2 %s ' \
                       '--expomap %s --ltcube %s --xml %s --emin %s ' \
                       '--emax %s --output_file %s --corner_plot %s ' \
                       '--n_samples %s --src %s --burn_in %s' % \
                       (FERMI_GW_ROOT, new_ft1, ft2, expomap, ltcube, xml, 
                        args.emin, args.emax, outul, outplot, args.n_samples, 
                        args.src, args.burn_in)

            try:
                _execute_command(cmd_line)
            except subprocess.CalledProcessError as err:
                print('ERROR: bayesian_ul.py skipped for RA=%.3f, DEC=%.3f'%\
                    (ra, dec))
                print(err)
                print(err.output)
                _chdir_rmdir(init_dir, subfolder_dir)
                continue
            pass
        
        # If do_tsmap option is 1 run the gtdotsmap script
        
        if args.do_tsmap == 1:
            #ts map
            rsp = glob.glob(args.datarepository + '/%s/*.rsp' % args.triggername)[0]
            expomap = os.path.basename(expomap)
            ltcube = os.path.basename(ltcube)
            #print('Using:\n %s,\n %s,\n %s,\n %s,\n %s' %\
            #    (xml, expomap, new_ft1, ltcube, rsp))
            outfits = os.path.join(init_dir, '%s_%.3f_%.3f_tsmap.fits' % \
                                 (args.triggername, ra, dec))
            print("Changing working directory to: %s" % subfolder_dir)
            os.chdir(subfolder_dir)
            
            ramax, decmax, tsmax = gtdotsmap.run(filteredeventfile=new_ft1, 
                ft2file=ft2, tsexpomap=expomap, tsltcube=ltcube, xmlmodel=xml, 
                rspfile=rsp, tsmap=outfits, step=0.8, side='auto', 
                clobber='yes', verbose='yes')[3:8:2]
            
            #save coordinates and ts value
            outfile = os.path.join(init_dir, '%s_%.3f_%.3f_coords.txt' % \
                                 (args.triggername, ra, dec))
            with open(outfile, 'w+') as f:
                f.write("#ra dec ts\n")
                f.write("%f %f %f\n" % (ramax, decmax, tsmax))
            
            #fits2png
            sources = [['Maximum TS', float(ramax), float(decmax)]]
            fits2png.fitsToPNG(outfits, outfits.replace('.fits', '.png'), 0.0,
                               tsmax, sources=sources)
            
            #count map
            outfits = os.path.join(init_dir, '%s_%.3f_%.3f_cmap.fits' % \
                                 (args.triggername, ra, dec))
            
            cmd_line = 'python %s/commands/gtdocountsmap.py ' \
                       'eventfile=%s rspfile=%s ft2file=%s ra=%s dec=%s '\
                       'rad=%s irf=%s zmax=%s tstart=%s tstop=%s emin=%s '\
                       'emax=%s skymap=%s thetamax=%s strategy=%s' % \
                       (GTBURST_PATH, new_ft1, rsp, ft2, ra, dec, args.roi, 
                        args.irf, args.zmax, args.tstarts, args.tstops, 
                        args.emin, args.emax, outfits, args.thetamax, 
                        args.strategy)
            _execute_command(cmd_line)
            
            #fits2png with sources
            sources = getSourcesInTheROI(ra, dec, args.roi, float(args.tstarts))
            fits2png.fitsToPNG(outfits, outfits.replace('.fits', '.png'), 
                               sources=sources)
            pass
        
        # See whether we need to run on simulated data

        if args.sim_ft1_tar is not None and args.sim_ft1_tar.lower() != 'none':

            tar_file_path = os.path.abspath(os.path.expandvars(args.sim_ft1_tar))

            assert os.path.exists(tar_file_path), "Tar file %s does not exist" % tar_file_path

            ts_outfile = os.path.join(init_dir, '%s_%.3f_%.3f_sim_TSs' % (args.triggername, ra, dec))

            cmd_line = 'python $GPL_TASKROOT/fermi_gw_toolkit/fermi_gw_toolkit/simulation_tools/measure_ts_distrib.py ' \
                       '--filtered_ft1 %s --ft2 %s ' \
                       '--expmap %s --ltcube %s --xmlfile %s --tar %s ' \
                       '--tsmap_spec %s --srcname GRB --outfile %s' %\
                       (new_ft1, ft2, expomap, ltcube, xml, tar_file_path, 
                        tsmap_spec, ts_outfile)

            print("")
            print("Changing working directory to: %s" % subfolder_dir)
            os.chdir(subfolder_dir)

            _execute_command(cmd_line)
            pass
        _chdir_rmdir(init_dir, subfolder_dir)
        print('Done!')
        
