import os
import numpy
import astropy.units as u
from astropy.coordinates import SkyCoord, get_moon, get_sun
from astropy.io import fits
from fermi_gw_toolkit import FERMISOURCECATALOG
from fermi_gw_toolkit.utils.date_to_met import met_to_utc

class lat_catalog:

	def __init__(self, file_path):
		data_pnt = fits.open(file_path)[1].data
		data_ext = fits.open(file_path)[2].data
		self.cat_ra = numpy.concatenate((data_pnt['RAJ2000'], 
										data_ext['RAJ2000']))
		self.cat_dec = numpy.concatenate((data_pnt['DEJ2000'], 
										 data_ext['DEJ2000']))
		self.cat_name = numpy.concatenate((data_pnt['Source_Name'],
										  data_ext['Source_Name']))
		self.cat_pos = SkyCoord(self.cat_ra*u.deg, self.cat_dec*u.deg,
								frame='icrs')
	def get_separation(self, pos):
		#error on source position or extension?
		return pos.separation(self.cat_pos) 
	
	def get_source_names(self, mask):
		return self.cat_name[mask]

	def get_source_coordinates(self, mask):
		src_ras = self.cat_ra[mask]
		src_decs = self.cat_dec[mask]
		return src_ras, src_decs

LAT_CATALOG = lat_catalog(FERMISOURCECATALOG)

def get_mask(ra, dec, radius):
	px_center = SkyCoord(ra*u.deg, dec*u.deg, frame='icrs')
	cat_sep = LAT_CATALOG.get_separation(px_center)
	mask = cat_sep < radius * u.deg
	return mask, cat_sep[mask].value

def check_catalog(ra, dec, radius):
	mask, src_sep = get_mask(ra, dec, radius)
	src_names = LAT_CATALOG.get_source_names(mask)
	return src_names, src_sep

def get_sun_moon(ra, dec, met, radius):
	utc = met_to_utc(met)
	px_center = SkyCoord(ra*u.deg, dec*u.deg, frame='icrs')
	moon_coord = get_moon(time=utc)
	sun_coord = get_sun(time=utc)
	moon_sep = moon_coord.separation(px_center.gcrs)
	sun_sep = sun_coord.separation(px_center.gcrs)
	sun = None
	if sun_sep < radius * u.deg:
		sun = ['Sun', sun_coord.ra.degree, sun_coord.dec.degree, sun_sep.value]
	moon = None
	if moon_sep < radius * u.deg:
		moon = ['Moon', moon_coord.ra.degree, moon_coord.dec.degree, 
				moon_sep.value]
	return sun, moon

def check_sun_moon(ra, dec, met, radius):
	sun, moon = get_sun_moon(ra, dec, met, radius)
	return sun is not None, moon is not None

def get_sources(ra, dec, radius):
	mask, src_sep = get_mask(ra, dec, radius)
	src_names = LAT_CATALOG.get_source_names(mask)
	src_ras, src_decs = LAT_CATALOG.get_source_coordinates(mask)
	return src_names, src_ras, src_decs, src_sep

def get_sources_roi(ra, dec, roi, met):
	sources = get_sources(ra, dec, roi)
	source_list = numpy.column_stack(sources).tolist()
	# source_list = []
	# for name, ra, dec, sep in zip(*sources):
	# 	source_list.append([str(name), float(ra), float(dec), float(sep)])
	sun, moon = get_sun_moon(ra, dec, met, roi)
	if sun is not None:
		source_list.append(sun)
	if moon is not None:
		source_list.append(moon)
	return source_list

if __name__=="__main__":
	ra = 208.77
	dec = -44.2
	radius = 3.
	met = 606088681.172 #2020-03-16 21:57:5
	print(check_catalog(ra, dec, radius))
	print(check_sun_moon(ra, dec, met, radius))
	print(get_sources_roi(ra, dec, radius*3, met))