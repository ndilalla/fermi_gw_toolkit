#!/usr/bin/env python

import argparse
import os
import shutil
import contextlib
import logging
import subprocess
import ConfigParser

from fermi_gw_toolkit.automatic_pipeline.utils import sanitize_filename

# Setup the FTOOLS so they can run non-interactively
from fermi_gw_toolkit.simulation_tools.setup_ftools import setup_ftools_non_interactive
setup_ftools_non_interactive()

# Setup logging
logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("find_GTI")
log.setLevel(logging.DEBUG)
log.info('find_GTI is starting')


@contextlib.contextmanager
def temp_directory(directory):

    directory = os.path.abspath(os.path.expandvars(os.path.expanduser(directory)))

    if not os.path.exists(directory):

        os.makedirs(directory)

    cur_dir = os.getcwd()

    os.chdir(directory)

    try:

        yield

    except:

        raise

    finally:

        os.chdir(cur_dir)

        shutil.rmtree(directory)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='one_likelihood')

    parser.add_argument("--config", help="Configuration file", type=str, required=True)
    parser.add_argument("--outputdir", help="Directory where to store the output results (must exist already)",
                        required=True, type=str)
    parser.add_argument("--tstarts", help="Start time of intervals to analyze", type=str, required=True)
    parser.add_argument("--tstops", help="Stop time of intervals to analyze", type=str, required=True)

    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read([sanitize_filename(args.config)])

    ra = float(config.get("cuts", "ra"))
    dec = float(config.get("cuts", "dec"))
    roi = float(config.get("cuts", "radius"))
    zmax = float(config.get("cuts", "zmax"))
    thetamax = float(config.get("cuts", "thetamax"))

    emin = float(config.get("cuts", "emin"))
    emax = float(config.get("cuts", "emax"))
    irf = config.get("cuts", "irf")

    galactic_model = config.get("likelihood", "galactic_model")
    particle_model = config.get("likelihood", "particle_model")
    tsmin = float(config.get("likelihood", "tsmin"))
    strategy = config.get("likelihood", "strategy")
    ulphindex = config.get("likelihood", "ulphindex")

    ft1 = config.get("data", "ft1")
    ft2 = config.get("data", "ft2")

    # Create temp directory

    workdir = "/scratch/giacomov_%s" % os.environ['LSB_JOBID']

    # Make sure it doesn't exist

    shutil.rmtree(workdir, ignore_errors=True)

    # Move there and copy the package

    with temp_directory(workdir):

        min_start = min(map(float, args.tstarts.split(",")))
        max_stop = max(map(float, args.tstops.split(",")))

        # Cut ft1 and ft2 to cover the needed interval
        temp_ft1 = "__temp_ft1.fit"

        cmd_line = "ftcopy '%s[EVENTS][(TIME >= %s) && (TIME <= %s)]' %s copyall=yes clobber=yes" % (ft1,
                                                                                                   min_start - 10000.0,
                                                                                                   max_stop + 10000.0,
                                                                                                   temp_ft1)

        log.info(cmd_line)
        subprocess.check_call(cmd_line, shell=True)

        temp_ft2 = "__temp_ft2.fit"

        cmd_line = "ftcopy '%s[SC_DATA][(STOP >= %s) && (START <= %s)]' %s copyall=yes clobber=yes" % (ft2,
                                                                                                     min_start - 10000.0,
                                                                                                     max_stop + 10000.0,
                                                                                                     temp_ft2)
        log.info(cmd_line)
        subprocess.check_call(cmd_line, shell=True)

        # Make package

        trigger_name = 'GRB'
        package_name = "bn%s" % trigger_name

        cmd_line = "rawdata2package.py ../%s ../%s %s %s %s %s" % (temp_ft1, temp_ft2, 0.0, trigger_name, ra, dec)

        os.makedirs(package_name)

        os.chdir(package_name)

        subprocess.check_call(cmd_line, shell=True)

        os.chdir("..")

        # Execute likelihood

        outfile = "%s_res.txt" % os.environ['LSB_JOBID']

        # Make sure that gtburst does not use the configuration file from the home
        os.environ['GTBURSTCONFDIR'] = os.getcwd()

        cmd_line = 'doTimeResolvedLike.py %s --outfile %s ' \
                   '--roi %s --tstarts %s --tstops %s --zmax %s --emin %s ' \
                   '--emax %s --irf %s --galactic_model %s ' \
                   '--particle_model "%s" --tsmin %s --strategy %s ' \
                   '--thetamax %s --datarepository %s --ulphindex %s --flemin 100 --flemax 1000 ' \
                   '--fgl_mode complete' % \
                   (package_name, outfile,
                    roi, args.tstarts, args.tstops, zmax, emin,
                    emax, irf, galactic_model,
                    particle_model, tsmin, strategy,
                    thetamax, os.getcwd(), ulphindex)
        log.info("About to execute:")
        log.info(cmd_line)

        subprocess.check_call(cmd_line, shell=True)

        # Move results to output dir
        outfile_dest = os.path.join(sanitize_filename(args.outputdir), outfile)
        shutil.copyfile(outfile, outfile_dest)

        log.info("Saved results into %s" % outfile_dest)