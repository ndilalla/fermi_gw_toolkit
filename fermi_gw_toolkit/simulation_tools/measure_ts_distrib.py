#!/usr/bin/env python

import argparse
import logging
import numpy as np

from fermi_gw_toolkit.automatic_pipeline.utils import sanitize_filename
from fermi_gw_toolkit.simulation_tools.fast_pylike import SimulationFeeder

# Configure logger
logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("measure_ts_distrib.py")
log.setLevel(logging.DEBUG)
log.info('measure_ts_distrib.py is starting')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='measure_ts_distrib')

    parser.add_argument('--filtered_ft1', required=True, type=str,
                        help='Path to the filtered ft1 for the ROI we want to simulate')

    parser.add_argument('--ft2', required=True, type=str, help="Path of ft2 file")

    parser.add_argument("--expmap", required=True, type=str, help="Path of the expomap")

    parser.add_argument("--ltcube", required=True, type=str, help="Path of the livetime cube")

    parser.add_argument("--xmlfile", required=True, type=str,
                        help="Path of the XML file with the result of the likelihood analysis")

    parser.add_argument("--tar", required=True, type=str,
                        help="Path of tar file containing the simulated ft1 files")

    parser.add_argument("--tsmap_spec", required=False, default=None, type=str,
                        help="Specification for TS map (default: None)")

    parser.add_argument("--srcname", required=False, default='GRB', type=str,
                        help="Name of target source")

    parser.add_argument("--outfile", required=True, type=str,
                        help="Name for the output file which will contain the numpy array of the TS values "
                             "measured on the simulations")

    args = parser.parse_args()

    ft1 = sanitize_filename(args.filtered_ft1)
    ft2 = sanitize_filename(args.ft2)
    expmap = sanitize_filename(args.expmap)
    ltcube = sanitize_filename(args.ltcube)
    xml_file = sanitize_filename(args.xmlfile)
    path_of_tar_file_with_simulated_ft1_files = sanitize_filename(args.tar)

    # This will process the simulations and compute the TSs

    sf = SimulationFeeder(ft1, ft2, expmap, ltcube, xml_file,
                          path_of_tar_file_with_simulated_ft1_files, args.tsmap_spec,
                          srcname=args.srcname)

    # Save TSs into a file
    outfile = sanitize_filename(args.outfile)
    np.save(outfile, sf.TSs)