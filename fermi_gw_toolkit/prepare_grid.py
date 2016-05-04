#!/usr/bin/env python

__author__ = 'giacomov'

import argparse
import os

import contour_finder
from check_file_exists import check_file_exists


if __name__=="__main__":

    desc = '''Generate a grid to be used for the TS map and the UL map, based on the contour of an input
              probability map in HEALPIX format. The input map must be normalized to 1'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--map',help='Input HEALPIX map', type=check_file_exists, required=True)
    parser.add_argument('--out_list',help='Name for the output text file with the list of (R.A., Dec.) pairs',
                        type=str, required=True)
    parser.add_argument('--out_map',help='Name for the output HEALPIX map with the new NSIDE',required=True, type=str)
    parser.add_argument('--nside',help='New NSIDE for the output grid',default=128, type=int)
    parser.add_argument('--cl',help='Containment level for the contour (default: 0.9, i.e., 90 percent)',default=0.9,type=float)

    args = parser.parse_args()

    my_finder = contour_finder.ContourFinder(args.map, args.nside)

    print("The intermediate map has an average pixel size of %.3f deg" % my_finder.pixel_size)

    indexes = my_finder.find_contour(args.cl)

    print("Found %s points within the %s percent containment level" % (indexes.shape[0], args.cl * 100.0))

    # Get R.A. and Dec for the pixels within the contour

    ra, dec = my_finder.get_sky_coordinates(indexes)

    # Write those in the output file

    with open(args.out_list, "w+") as f:

        f.write("#RA Dec\n")

        for r,d in zip(ra,dec):

            f.write("%s %s\n" % (r,d))

    my_finder.write_map(args.out_map)

