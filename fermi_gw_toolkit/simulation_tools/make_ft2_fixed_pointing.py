#!/usr/bin/env python

import argparse
import astropy.io.fits as pyfits
import logging
import numpy as np
import os

from fermi_gw_toolkit.automatic_pipeline.utils import sanitize_filename

from astropy.coordinates.angle_utilities import angular_separation

from GtBurst.angularDistance import getAngularDistance


# Configure logger
logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger(os.path.basename(__file__))
log.setLevel(logging.DEBUG)
log.info('%s is starting' % (os.path.basename(__file__)))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce an FT2 file with the pointing fixed at the given position')

    parser.add_argument("--all_mission_ft2", help="Path to the mission-long FT2 file", type=str, required=True)
    parser.add_argument("--ra", help='R.A. of the desired pointing', type=float, required=True)
    parser.add_argument("--dec", help='Dec. of the desired pointing', type=float, required=True)
    parser.add_argument("--met_start", help='MET of the start of the new FT2 file', type=float, required=True)
    parser.add_argument("--met_stop", help='MET of the stop of the new FT2 file', type=float, required=True)
    parser.add_argument("--outfile", help='Output FT2 file', type=str, required=True)

    args = parser.parse_args()

    # Read the FT2 file and find the time interval where the pointing was as close as possible to the
    # desired one

    all_mission_ft2 = sanitize_filename(args.all_mission_ft2)

    with pyfits.open(all_mission_ft2) as f:

        # Is this a 30s FT2 file or a 1s FT2 file?
        dt_ = f['SC_DATA'].data.field("STOP") - f['SC_DATA'].data.field("START")

        if np.average(dt_) >= 10.0:

            # 30 s FT2 file
            dt = 30.0

        else:

            dt = 1.0

        log.info("Probed that this is a %i s FT2 file" % dt)

        # Compute how many entries do we need
        n_entries = (args.met_stop - args.met_start) / dt

        if not n_entries.is_integer():

            n_entries = int(n_entries)

            stop_time = args.met_start + int(n_entries) * dt

            log.warn("WARNING: the requested duration for the FT2 file is not a multiple of %s. "
                     "Truncating to %s" % (dt, stop_time))

        else:

            n_entries = int(n_entries)

            stop_time = args.met_stop

        log.info("Computing angular distance between pointing in the pointing history and "
                 "desired position (%s, %s)..." % (args.ra, args.dec))

        # Compute angular distance between desired (RA, Dec) and the pointing of the LAT

        ra_scz, dec_scz = f['SC_DATA'].data.field("RA_SCZ"), f['SC_DATA'].data.field("DEC_SCZ")

        ang_dis = getAngularDistance(args.ra, args.dec, ra_scz, dec_scz)

        # Find the time where the distance was at its minimum (keeping some margin to later select the data)
        min_idx = ang_dis[:-n_entries].argmin()

        time_of_min_distance = f['SC_DATA'].data.field("START")[min_idx]

        log.info("At MET = %.3f the distance between the pointing and the "
                 "input position was %.3f deg" % (time_of_min_distance, ang_dis[min_idx]))

        # Now create a new FT2 file with the pointing fixed at the desired position

        new_sc_table = pyfits.BinTableHDU(f['SC_DATA'].data[min_idx:min_idx + n_entries])

        new_sc_table.data.RA_SCZ[:] = new_sc_table.data.RA_SCZ[0]
        new_sc_table.data.DEC_SCZ[:] = new_sc_table.data.DEC_SCZ[0]
        new_sc_table.data.RA_SCX[:] = new_sc_table.data.RA_SCX[0]
        new_sc_table.data.DEC_SCX[:] = new_sc_table.data.DEC_SCX[0]

        new_sc_table.data.RA_ZENITH[:] = new_sc_table.data.RA_ZENITH[0]
        new_sc_table.data.DEC_ZENITH[:] = new_sc_table.data.DEC_ZENITH[0]

        new_sc_table.data.RA_NPOLE[:] = new_sc_table.data.RA_NPOLE[0]
        new_sc_table.data.DEC_NPOLE[:] = new_sc_table.data.DEC_NPOLE[0]

        new_sc_table.data.ROCK_ANGLE[:] = new_sc_table.data.ROCK_ANGLE[0]

        new_sc_table.data.START = np.arange(args.met_start, stop_time, dt)
        new_sc_table.data.STOP = np.arange(args.met_start + dt, stop_time + dt, dt)

        new_sc_table.header.update(f['SC_DATA'].header)

        new_sc_table.writeto(args.outfile)