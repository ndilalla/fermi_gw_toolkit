#!/usr/bin/env python

__author__ = 'giacomov'

import argparse
from astropy.io import fits
from reproject import reproject_from_healpix

from fermi_gw_toolkit.utils.check_file_exists import check_file_exists


if __name__== "__main__":

    desc = '''Convert a HEALPIX map into a WCS (projected) one'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--in_map',help='Input HEALPIX map', type=check_file_exists, required=True)
    parser.add_argument('--out_map',help='Name for the output map', type=str, required=True)
    parser.add_argument('--ra',help='R.A. of center of map',type=float, required=True)
    parser.add_argument('--dec',help='Dec. of center of map',type=float, required=True)

    args = parser.parse_args()

    target_header = fits.Header.fromstring("""
NAXIS   =                    2
NAXIS1  =                 1000
NAXIS2  =                  800
CTYPE1  = 'RA---AIT'
CRPIX1  =                  500
CRVAL1  =             %s
CDELT1  =                 -0.4
CUNIT1  = 'deg     '
CTYPE2  = 'DEC--AIT'
CRPIX2  =                  400
CRVAL2  =              %s
CDELT2  =                  0.4
CUNIT2  = 'deg     '
COORDSYS= 'icrs    '
""" % (args.ra, args.dec), sep='\n')

    array, footprint = reproject_from_healpix(args.in_map, target_header)

    fits.writeto(args.out_map, array, header=target_header)


