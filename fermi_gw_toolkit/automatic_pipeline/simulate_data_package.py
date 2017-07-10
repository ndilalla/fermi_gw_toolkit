#!/usr/bin/env python

import argparse
import logging
import os
import glob

import astropy.io.fits as pyfits

from utils import sanitize_filename
from full_sky_simulation import CustomSimulator

# Configure logger
logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("simulate_data_package.py")
log.setLevel(logging.DEBUG)
log.info('simulate_data_package.py is starting')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='simulate_data_package')

    parser.add_argument('--package_path', required=True, type=str,
                        help='Path of the gtburst package to simulate')
    parser.add_argument('--duration', required=True, type=float, help="Duration of the simulation")
    parser.add_argument("--outdir", required=True,
                        help="Directory for the output package. The last path element will be used as trigger name "
                             "for the new package")
    parser.add_argument("--seed", required=False, default=None, type=int, help="Seed for the simulation")
    parser.add_argument("--emin", required=False, default=100.0, type=float, help="Minimum energy")
    parser.add_argument("--emax", required=False, default=100000.0, type=float, help="Maximum energy")

    args = parser.parse_args()

    # Read from the data package the trigger time and trigger name

    package_path = sanitize_filename(args.package_path)

    assert os.path.exists(package_path) and os.path.isdir(package_path), \
        "Path %s does not exist or it is not a directory" % package_path

    trigger_name = os.path.split(package_path)[-1]

    # Find response files (.rsp) (there might be more than one because there could be more than one version)

    response_file_pattern = os.path.join(package_path, "gll_cspec_tr_%s_v*.rsp" % trigger_name)

    response_files = glob.glob(response_file_pattern)

    assert len(response_files) > 0, "Could not find response file %s" % response_file_pattern

    # Sort them
    response_files = sorted(response_files)

    with pyfits.open(response_files[-1]) as rsp:

        trigger_time = rsp[0].header['UREFTIME']
        ra_obj = rsp[0].header['RA_OBJ']
        dec_obj = rsp[0].header['DEC_OBJ']

    # Find FT2 file
    ft2_file_pattern = os.path.join(package_path, "gll_ft2_tr_%s_v*.fit" % trigger_name)

    ft2_files = glob.glob(ft2_file_pattern)

    assert len(ft2_files) > 0, "Could not find any ft2 files like %s" % ft2_file_pattern

    # Sort them
    ft2_files = sorted(ft2_files)

    ft2_file = ft2_files[-1]

    # Simulate
    simulator = CustomSimulator(ft2_file, trigger_time, args.duration, emin=args.emin, emax=args.emax)

    simulator.run_simulation("__my_sim.fits", seed=args.seed)

    simulator.run_gtdiffrsp()

    output_path = sanitize_filename(args.outdir)

    new_trigger_name = os.path.split(output_path)[-1]

    simulator.make_data_package_files(new_trigger_name, ra=ra_obj, dec=dec_obj, destination_dir=output_path)