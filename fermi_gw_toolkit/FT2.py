#!/usr/bin/env python
import scipy as sp
from astropy.io import fits
import astropy.coordinates as coord
from astropy import units as u

def angsep(x1,y1,x2,y2):
    #    """
    #    spherical angle separation, aka haversine formula  
    #    input and output are in degrees               
    #    """
    dlat = sp.radians(y2 - y1)
    dlon = sp.radians(x2 - x1)
    y1 = sp.radians(y1)
    y2 = sp.radians(y2)
    a = sp.sin(dlat/2.)*sp.sin(dlat/2.) + sp.cos(y1)*sp.cos(y2)*sp.sin(dlon/2.)*sp.sin(dlon/2.)
    #if a<0 or a>1.: print 'a:',a,x1,y1,x2,y2,dlat,dlon,'!!!!!'
    try:
        c  = 2*sp.arctan2(sp.sqrt(a), sp.sqrt(1.-a))
    except:
        print '!!!:',a,x1,y1,x2,y2,dlat,dlon,'!!!!!'
        c=0
        pass
    return sp.degrees(c)

class FT2:
    def __init__(self,ft2file,tmin,tmax):
        hdulist=fits.open(ft2file)    
        SC_data=hdulist['SC_DATA'].data
        SC_data=hdulist['SC_DATA'].data
        # TIME
        TIME_ALL=SC_data.field('START')
        FILTER  =sp.logical_and(TIME_ALL>tmin,TIME_ALL<tmax)
        self.SC_TSTART     = SC_data.field('START')[FILTER]
        self.SC_TSTOP      = SC_data.field('STOP')[FILTER]
        self.NENTRIES      = len(self.SC_TSTART)
        # BORESIGHT:
        self.RA_SCZ    = SC_data.field('RA_SCZ')[FILTER]
        self.DEC_SCZ   = SC_data.field('DEC_SCZ')[FILTER]
        # ZENITH
        self.RA_ZENITH   = SC_data.field('RA_ZENITH')[FILTER]
        self.DEC_ZENITH  = SC_data.field('DEC_ZENITH')[FILTER]
        # SAA
        self.IN_SAA      = SC_data.field('IN_SAA')[FILTER]

        self.IDX_ARRAY   = sp.arange(self.NENTRIES)
        self.FOV_ARRAY   = sp.zeros(self.NENTRIES)
        self.theta_max=65
        self.zenith_max=90
        print 'In FT2 file %s found %d entries' %(ft2file,self.NENTRIES)
        pass

    def fov(self,theta_max,zenith_max):
        self.theta_max=theta_max
        self.zenith_max=zenith_max
        pass
    
    def getIndex(self,time):
        if (self.SC_TSTOP[0]>time):
            print 'FT2 does not cover the trigger time!'
            return 0
        return sp.argmax(self.SC_TSTOP[self.SC_TSTOP<time])

    def getTime(self,idx):
        return self.SC_TSTART[idx],self.SC_TSTOP[idx]

    def getTheta(self,idx,ra,dec):
        return angsep(ra,dec,self.RA_SCZ[idx],self.DEC_SCZ[idx])

    def getZenith(self,idx,ra,dec):
        return angsep(ra,dec,self.RA_ZENITH[idx],self.DEC_ZENITH[idx])
    
    def getThetaTime(self,ra,dec):
        return angsep(ra,dec,self.RA_SCZ,self.DEC_SCZ)

    def getZenithTime(self,ra,dec):
        return angsep(ra,dec,self.RA_ZENITH,self.DEC_ZENITH)

    def inFovTime(self,ra,dec):
        theta=self.getThetaTime(ra,dec)
        zenith=self.getZenithTime(ra,dec)
        return sp.logical_and(sp.logical_and(theta<self.theta_max,zenith<self.zenith_max),self.IN_SAA==0)

    def getEntryExitTime(self,ra,dec,t0):
        idx0=self.getIndex(t0)        
        infov=self.inFovTime(ra,dec)
        theta=self.getThetaTime(ra,dec)
        zenith=self.getZenithTime(ra,dec)        
        start=self.SC_TSTART-t0
        stop=self.SC_TSTOP-t0
        infov_t0=infov[idx0]
        
        if infov_t0:  t_0 = stop[sp.logical_and(infov==0,stop<0)][-1]

        else:         t_0 = start[sp.logical_and(infov==1,start>0)][0]
        t_1 = start[sp.logical_and(infov==0,stop>t_0)][0]
        t_1 = stop[self.getIndex(t0+t_1)]
        #if stop[ii_1+1] > stop[ii_1]+60: t_1 = stop[ii_1]
        #print '%10.3f %10.3f %5d %10.3f %10.3f %10.3f %10.3f ' %(ra,dec,ii_1,stop[ii_1],stop[ii_1+1],t_0,t_1)
        return t_0,t_1 

    def inFov(self,idx,ra,dec):
        theta=self.getTheta(idx,ra,dec)
        zenith=self.getZenith(idx,ra,dec)
        return sp.logical_and(theta<self.theta_max,zenith<self.zenith_max)


    def fov_array(self,ra,dec):
        Npoints=len(ra)
        self.FOV_ARRAY=[]
        for i in self.IDX_ARRAY:
            #print i,self.getTime(i)
            self.FOV_ARRAY.append(self.inFov(i,ra,dec))
            pass
        self.FOV_ARRAY=sp.array(self.FOV_ARRAY)
        pass
    
    def condition1(self,t0):
        print self.FOV_ARRAY.shape
        print (self.FOV_ARRAY<0).shape
        print self.SC_TSTOP.shape
        print (self.SC_TSTOP>t0).shape
        
        print sp.logical_and(self.FOV_ARRAY<0,self.SC_TSTOP>t0)[0]
                
    def getTimeInterval(self, idx, ra1, dec1):
        idx0=0
        idx1=0
        
        if self.inFov(idx,ra1,dec1):
            while self.inFov(idx,ra1,dec1):
                idx-=1
                pass
            idx0=idx
            idx+=1
        else:
            while not self.inFov(idx,ra1,dec1):
                idx+=1
                pass
            idx0=idx
            pass
        while self.inFov(idx,ra1,dec1):
            idx+=1
            pass
        idx1=idx
        return self.getTime(idx0),self.getTime(idx1)
    
    def getTimeIntervalArray(self, time, ra, dec):        
        idx=self.getIndex(time)
        entry_exits=[]
        i=0
        for ra1,dec1 in zip(ra,dec):
            i+=1
            print i
            entry_exits.append(self.getTimeInterval(idx, ra1, dec1))
            pass
        return entry_exits
        
