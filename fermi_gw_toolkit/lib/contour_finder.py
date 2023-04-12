__author__ = 'giacomov'

import numpy as np
import healpy as hp
import matplotlib.pyplot as plt


def pix_to_sky(idx, nside):
    """Convert the pixels corresponding to the input indexes to sky coordinates (RA, Dec)"""

    theta, phi = hp.pix2ang(nside, idx)

    ra = np.rad2deg(phi)
    dec = np.rad2deg(0.5 * np.pi - theta)

    return ra, dec

def sky_to_pix(ra,dec, nside):
    """Convert the pixels corresponding to the input indexes to sky coordinates (RA, Dec)"""
    phi    = np.deg2rad(ra)
    theta  = 0.5 * np.pi - np.deg2rad(dec)

    idx = hp.ang2pix(nside, theta, phi)

    return idx

def check_power_of_two(num):
    """Check that the given number is a power of 2"""

    return num != 0 and ((num & (num - 1)) == 0)


class ContourFinder(object):

    def __init__(self, healpix_map, nside=128):

        self._nside = nside

        if not check_power_of_two(self.nside):

            raise RuntimeError("nside must be a power of 2.")

        hpx_orig, header = hp.read_map(healpix_map, h=True)

        # Use power=-2 so the sum is still 1

        self._ligo_map = hp.pixelfunc.ud_grade(hpx_orig, nside_out=self.nside, power=-2)

        # Check that the total probability is still equal to the input map

        assert abs(np.sum(hpx_orig) - np.sum(self.map)) < 1e-3, "Total probability after resize has not been kept!"

    @property
    def map(self):
        """Return the resized map"""

        return self._ligo_map

    @property
    def nside(self):
        """Return the nside of the re-sized map"""
        return self._nside

    @property
    def pixel_size(self):
        """Return average side of pixel in degrees for the re-sized map"""

        # Formula from the manual of the function HEALPIXWINDOW

        arcmin_to_degree = 1.0 / 60.0

        return np.sqrt( 3.0 / np.pi) * 3600.0 / self.nside * arcmin_to_degree

    def write_map(self, outfile, coordinate_type='C'):
        """Write map to disk. By default the coordinate system is Celestial (equatorial).
        See healpix documentation for the accepted formats"""

        hp.write_map(outfile, self.map, coord=coordinate_type)

    def find_contour(self, containment_level=0.9):
        """Return the *indexes* of the pixels in the map within the given containment level"""

        # Get indexes sorting the array in decreasing order

        index_revsort = np.argsort(self._ligo_map)[::-1]

        # Compute the cumulative sum of the probabilities in the ordered "space"

        cumsum = np.cumsum(self._ligo_map[index_revsort])

        # Find out which pixels are within the containment level requested in the ordered "space"
        
        idx_prime = (cumsum <= containment_level)

        # Convert back to the "unordered space"

        idx = index_revsort[idx_prime]
        
        cum_tot = np.sum(self._ligo_map[idx])
        if abs(cum_tot - containment_level) > 1e-2:
            print("WARNING: Total prob. within containment (%.3f) is too far from requested value (%.3f)" % (cum_tot, containment_level))

        return idx

    def display(self, indexes):

        copy_of_map = np.copy(self.map)

        copy_of_map[indexes] = 1.0

        fig = plt.figure()

        hp.mollview(copy_of_map, title="Mollview image RING")

        return fig

    def get_sky_coordinates(self, indexes):

        ra, dec = pix_to_sky(indexes, self.nside)

        return ra, dec
