import healpy as hp
import numpy as np


def sky_to_healpix_id(nside, this_ra, this_dec):

    theta = 0.5 * np.pi - np.deg2rad(this_dec)
    phi = np.deg2rad(this_ra)
    ipix = hp.ang2pix(nside, theta, phi)

    return ipix
