import astropy.io.fits as pyfits
from astropy.time import Time
from GtBurst.dataHandling import date2met, met2date

def get_met(ligo_map):
    hdulist = pyfits.open(ligo_map)
    date_obs = hdulist[1].header['DATE-OBS']
    date_obs = '%s %s' %(date_obs[:10], date_obs[11:])
    return date2met(date_obs)

def met_to_utc(met):
    date = met2date(met)
    return Time(date, scale='utc')
