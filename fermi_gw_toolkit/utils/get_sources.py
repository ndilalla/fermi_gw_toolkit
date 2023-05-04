import os
from astropy.io import fits as pyfits
from GtBurst.angularDistance import getAngularDistance
from GtBurst import sunpos

from fermi_gw_toolkit import FERMISOURCECATALOG

FGL_CLASSES = ['HMB','hmb','NOV','nov','BZB','bzb','BZQ','bzq','AGN','agn',
               'SEY','sey','AGU','agu','SBG','sbg','PSR','psr','PWN','pwn',
               'SNR','snr']

def getSourcesInTheROI(ra, dec, roi, met):
  roi = float(roi)
  #config = fermiatSUlib.Configuration() 
  # xml = readXml.SourceModel(config['FGL_XML_CATALOG'])
  # fglSources = {k: v for k, v in xml.srcList.iteritems() if k.find("2FGL")>=0}
  
  #Open the FITS file, keeping only certain classes of sources
  f = pyfits.open(os.environ['FERMISOURCECATALOG'])
  fglFITS = f['LAT_Point_Source_Catalog'].data
  f.close()

  classesToKeep = FGL_CLASSES
  def filtering(x):
    if(x.field('CLASS1') in classesToKeep):
      return True
    else:
      return False
    pass
  pass
  
  fglSources= filter(filtering,fglFITS)  
  sources = []  
  for src in fglSources:
    try:
      thisRA = float(src.field("RAJ2000"))
      thisDec = float(src.field("DEJ2000"))
      thisDistance = getAngularDistance(float(ra),float(dec),thisRA,thisDec)
    except:
      #Extended sources
      continue
    if(thisDistance <= roi):
      if(src.field('ASSOC1')!=""):
        k = "%s\n(%s)" %(src.field("ASSOC1"),src.field("CLASS1"))
      else:
        k = "%s\n(%s)" % (src.field("Source_Name"),src.field("CLASS1"))
      sources.append([k,thisRA,thisDec,thisDistance])
  pass
  
  #Now add the Sun, if it is inside the ROI
  sundir = sunpos.getSunPosition(met)
  ra_sun, dec_sun = (sundir.ra(),sundir.dec())
  sunDistance = getAngularDistance(float(ra),float(dec),ra_sun,dec_sun)
  if(sunDistance <= roi):
    k = "Sun pos. at\ntrigger time"
    sources.append([k,ra_sun,dec_sun,sunDistance])
  pass
  return sources

def getClosestPointSource(sources):
  if(len(sources)==0):
    return [None,0,0,0]
  else:
    return min(sources,key=lambda x:x[3])
  pass
  return index, error
