#!/usr/bin/env python
import os, subprocess
import socket
import sys
from astropy.io import fits as pyfits

from GtBurst.dataHandling import runShellCommand

classname={'P8R2_TRANSIENT100E_V6':'Transient100E',
	   'P8R2_TRANSIENT100_V6':'Transient100',
	   'P8R2_TRANSIENT020E_V6':'Transient020E',
	   'P8R2_TRANSIENT020_V6':'Transient020',
	   'P8R2_TRANSIENT010E_V6':'Transient010E',
	   'P8R2_TRANSIENT010_V6':'Transient010',
	   'P8R2_SOURCE_V6':'Source',
	   'P8R2_CLEAN_V6':'Clean',
	   'P8R2_ULTRACLEAN_V6':'UltraClean',
	   'P8R2_ULTRACLEANVETO_V6':'UltraCleanVeto',
	   'P8R2_TRANSIENT100S_V6':'Transient100S',
	   'P8R2_TRANSIENT015S_V6':'Transient015S',
	   'P7REP_TRANSIENT_V15':'Transient',
	   'P7REP_SOURCE_V15':'Source',
	   'P7REP_CLEAN_V15':'Clean',
	   'P7REP_ULTRACLEAN_V15':'UltraClean'
	   }


def checkFILES(ft1,ft2,tstart, tend):
	print("Checking FT1 file...")
	ft1_data = pyfits.open(ft1)[1].data
	TIME     = ft1_data.TIME
	DT=tend-TIME.max()
	if DT>60.: print("====> FT1 file probably incomplete. %.1f" % DT)
	else: print("====> FT1 file complete. %.1f" % DT)
	print("Checking FT2 file...")
	ft2_data = pyfits.open(ft2)[1].data
	STOP     = ft2_data.STOP
	DT=tend-STOP.max()
	if DT>60.: print("====> FT2 file probably incomplete. %.1f" % DT)
	else: print("====> FT2 file complete. %.1f" % DT)
	pass

def getFilesAstroServer(name, tstart, tend, outdir, emin, emax, sample,
			ResponseFunction, chatter=1, OneSec=True, Type=3,
			**kwargs):
	
	sampleFT1 = sample
	sampleFT2 = sample
	OneSec = int(OneSec)

	ft1name = '%s_%s_ft1_%.0f_%.0f.fits' %(name, sampleFT1, tstart, tend)
	ft2name = '%s_%s_ft2_%.0f_%.0f.fits' %(name, sampleFT2, tstart, tend)

	finalFile_ft1 = '%s/%s' %(outdir, ft1name)
	finalFile_ft2 = '%s/%s' %(outdir, ft2name)
	
	#Decide if we are running locally at SLAC or not
	hostname = socket.getfqdn() # this is thefully qualified domain name
	run_at_slac=1
	if hostname.find("slac.stanford.edu")==-1:
		run_at_slac=0
        pass

	if (run_at_slac):
		cmd1='~glast/astroserver/prod/astro --event-sample %s --output-ft1 %s --minTimestamp %s --maxTimestamp %s store ' % (sampleFT1,finalFile_ft1,tstart,tend)
		if OneSec==1:
			cmd2='~glast/astroserver/prod/astro --event-sample %s --output-ft2-1s %s --minTimestamp %s --maxTimestamp %s storeft2 ' % (sampleFT2,finalFile_ft2,tstart,tend)
		else:
			cmd2='~glast/astroserver/prod/astro --event-sample %s --output-ft2-30s %s --minTimestamp %s --maxTimestamp %s storeft2 ' % (sampleFT2,finalFile_ft2,tstart,tend)
		
		#apply extra Transient-class cut to P7 data
		try:
			cmd1+=' --event-class-name %s' %(classname[ResponseFunction])
			print "Applying extra %s cut for %s IRFS taken from the %s repository" % (classname[ResponseFunction],ResponseFunction,sampleFT1)
			pass
		except:
			pass
			
		if (Type==1 or Type==3):
			if os.path.exists(finalFile_ft1):
				print 'Using existing file %s' % finalFile_ft1
			else:
				if chatter>0:
					print cmd1
				runShellCommand(cmd1)
				pass
			if chatter>0:
				print '--> file FT1: %s' % finalFile_ft1
			pass
		
		if (Type==2 or Type==3):
			if os.path.exists(finalFile_ft2):
				print 'Using existing file %s' % finalFile_ft2
			else:
				if chatter>0:
					print cmd2
				runShellCommand(cmd2)
				# cmd2='mv %s %s' %(ft2name,finalFile_ft2)
				# runShellCommand(cmd2)
				pass
			if chatter>0:
				print '--> file FT2: %s' % finalFile_ft2
			pass
		pass
	
	else:
			
		if not (os.path.exists(finalFile_ft1) and os.path.exists(finalFile_ft2)):
			print "\n\nYou are running on a computer that is not in the SLAC network."
			print "HOSTNAME = %s " % hostname
			#print "We may need to ssh to slac to talk to the astroserver...Please login if asked (you may be asked twice)..\n\n"
			message = "The download feature has not been implemented on local computer yet. Please download the FT1 and FT2 files manually and include them in configuration file.\n\n"
			sys.exit(message)
				
		"""
		cmd1='ssh rhel6-64.slac.stanford.edu \"~glast/astroserver/prod/astro --event-sample %s --output-ft1 /tmp/%s --minTimestamp %s --maxTimestamp %s store ' % (sampleFT1,ft1name,tstart,tend)
		
		if OneSec==1:
			cmd2='ssh rhel6-64.slac.stanford.edu \"~glast/astroserver/prod/astro --event-sample %s --output-ft2-1s /tmp/%s --minTimestamp %s --maxTimestamp %s storeft2 \"' % (sampleFT2,ft2name,tstart,tend)
		else:
			cmd2='ssh rhel6-64.slac.stanford.edu \"~glast/astroserver/prod/astro --event-sample %s --output-ft2-30s /tmp/%s --minTimestamp %s --maxTimestamp %s storeft2 \"' % (sampleFT2,ft2name,tstart,tend)
		
		#apply extra Transient-class cut to P7 data
		try:
			cmd1+=' --event-class-name %s' %(classname[ResponseFunction])
			print "Applying extra %s cut for %s IRFS taken from the %s repository" % (classname[ResponseFunction],ResponseFunction,sampleFT1)
			pass
		except:
			pass
	
		#if 'TRANSIENT' in ResponseFunction:
		#	cmd1+=' --event-class-name Transient "'
		#	print "Applying extra Transient-class cut to P7TRANSIENT data taken from the %s repository" %sampleFT1
		#else: cmd1+='"'
		
		if (Type==1 or Type==3):
			if os.path.exists(finalFile_ft1):
				print 'Using existing file %s' % finalFile_ft1
			else:
				if chatter>0:
					print "-----------------------------------"
				rsync_cmd='rsync -pave ssh --progress rhel6-64.slac.stanford.edu:/tmp/%s %s' %(ft1name,finalFile_ft1)
				runShellCommand(cmd1+";"+rsync_cmd)
				runShellCommand('ssh rhel6-64.slac.stanford.edu \"rm /tmp/%s\"' %(ft1name))
			if chatter>0:
				print "-----------------------------------\n\n"
				print '--> file FT1: %s' % finalFile_ft1
	
		if (Type==2 or Type==3):
			if os.path.exists(finalFile_ft2):
				print 'Using existing file %s' % finalFile_ft2
			else:
				if chatter>0:
					print "-----------------------------------"
				rsync_cmd='rsync -pave  ssh --progress rhel6-64.slac.stanford.edu:/tmp/%s %s' %(ft2name,finalFile_ft2)
				runShellCommand(cmd2+";"+rsync_cmd)
				runShellCommand('ssh rhel6-64.slac.stanford.edu \"rm /tmp/%s\"' %(ft2name))
			if chatter>0:
				print "-----------------------------------"
				print '--> file FT2 %s' % finalFile_ft2
		"""
	
	if (os.path.exists(finalFile_ft1)==False):
		print 'For some reason we could not obtain the FT1 file....'
		pass
	if (os.path.exists(finalFile_ft2)==False):
		print 'For some reason we could not obtain the FT2 file....'
		pass
	
	return finalFile_ft1, finalFile_ft2
