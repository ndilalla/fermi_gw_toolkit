import astropy.io.fits as pyfits
from GtBurst.dataHandling import date2met

def get_met(ligo_map):
    hdulist = pyfits.open(ligo_map)
    date_obs = hdulist[1].header['DATE-OBS']
    date_obs = '%s %s' %(date_obs[:10], date_obs[11:])
    return date2met(date_obs)


