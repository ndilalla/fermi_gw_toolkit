#!/usr/bin/env python

import argparse
import ConfigParser
import GtApp
import re
import json
import logging
import astropy.io.fits as pyfits

from fermi_gw_toolkit.automatic_pipeline.utils import sanitize_filename


logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("find_GTI")
log.setLevel(logging.DEBUG)
log.info('find_GTI is starting')


def find_ROI_cut(ft1):

    # We cannot use the pyLike.RoiCuts() because it fails on files produced by the astroserver
    header = pyfits.getheader(ft1, "EVENTS")

    # Find DSTYPE keywords
    dstypes = filter(lambda x:x.find("DSTYP")==0, header.keys())

    ra, dec, radius = (None, None, None)

    # Find POS cut
    for dstype in dstypes:

        if header[dstype].find("POS") == 0:

            id = dstype.replace("DSTYP", "")

            dsval = header["DSVAL%s" % id]

            assert dsval.find("circle") == 0

            groups = re.findall("circle\(([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?),\s?([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?),\s?([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)\)", dsval)

            ra, dec, radius = float(groups[0][0]), float(groups[0][4]), float(groups[0][8])


    assert ra is not None

    return ra, dec, radius

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find Good Time Intervals with gtmktime')

    parser.add_argument("--config", help="Configuration file", type=str, required=True)
    parser.add_argument("--gtifile", help="Name of output GTI file (text format)", type=str, required=True)

    args = parser.parse_args()

    # Read configuration file
    config = ConfigParser.SafeConfigParser()
    config.read([sanitize_filename(args.config)])

    ft1 = sanitize_filename(config.get("data", "ft1"))
    ft2 = sanitize_filename(config.get("data", "ft2"))

    # Read from the original FT1 the ROI definition

    ra_center, dec_center, radius = find_ROI_cut(ft1)

    log.info("Found ROI in file. Center: (R.A., Dec) = (%s, %s), radius = %s deg" % (ra_center, dec_center, radius))

    assert ra_center == float(config.get("cuts", "ra"))
    assert dec_center == float(config.get("cuts", "dec"))
    assert radius == float(config.get("cuts", "radius"))

    # Make FILTER expression

    gtmktime_filter = "(DATA_QUAL>0 || DATA_QUAL==-1) && LAT_CONFIG==1 && IN_SAA!=T && LIVETIME>0 "

    zmax = float(config.get("cuts", "zmax"))
    thetamax = float(config.get("cuts", "thetamax"))

    if zmax != 180.0:

        gtmktime_filter += " && (ANGSEP(RA_ZENITH,DEC_ZENITH, %s, %s) <= (%s-%s))" % (ra_center, dec_center,
                                                                                      zmax, radius)

    if thetamax != 180.0:

        gtmktime_filter += " && (ANGSEP(RA_SCZ,DEC_SCZ,%s,%s) <= %s - %s)" % (ra_center, dec_center,
                                                                              thetamax, radius)

    log.info("Applying the following filter:")
    log.info(gtmktime_filter)

    outfile = "__temp_gti.fit"

    gtmktime = GtApp.GtApp("gtmktime")

    gtmktime.run(scfile=ft2,
                 filter=gtmktime_filter,
                 roicut='no',
                 evfile=ft1,
                 outfile=outfile,
                 apply_filter="yes",
                 overwrite="yes",
                 header_obstimes="yes",
                 clobber="yes")

    # Open GTI file and read in GTIs
    gti = pyfits.getdata(outfile, "GTI")

    outdata = sanitize_filename(args.gtifile)

    gtis = map(lambda x:(x[0], x[1]), zip(gti.field("START"), gti.field("STOP")))

    # Sort GTIs
    gtis = sorted(gtis, key=lambda x:x[0])

    # Write them in outfile

    out_d = {}
    out_d['starts'] = []
    out_d['stops'] = []

    for start, stop in gtis:

        if (stop - start) >= float(config.get("GTI", "minimum_duration")):

            out_d['starts'].append(start)
            out_d['stops'].append(stop)

    with open(outdata, "w+") as f:

        json.dump(out_d, f)

    log.info("Written %s GTIs in file %s" % (len(out_d['starts']), outdata))
