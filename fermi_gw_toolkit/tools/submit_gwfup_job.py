import os
import sys
import time
import socket
import argparse, glob

from astropy.io import fits
from datetime import datetime
from GtBurst.dataHandling import date2met
from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.bin.download_LAT_data import download_LAT_data
from fermi_gw_toolkit.utils.check_ft1_ft2_files import check_ft1_ft2_files
from fermi_gw_toolkit.utils.gcn_info import curl_s3df

def getfromfile(filename):
    cmd='chmod a+r %s' % filename
    os.system(cmd) 
    f=fits.open(filename)
    date_obs=f[1].header['DATE-OBS'].replace('T',' ')
    met=float(date2met(date_obs))
    name=filename.split('/')[-1].split('.')[0]
    trigger_name='bn%s' % name
    print(trigger_name, date_obs, met)
    return trigger_name, filename, met
    
def getfromweb(url):
    # https://gracedb.ligo.org/api/superevents/S190706ai/files/LALInference.offline.fits.gz
    name = url.replace('https://gracedb.ligo.org/api/superevents/','').split('/files/')[0]
    extension  = url.replace('https://gracedb.ligo.org/api/superevents/','').split('/files/')[-1].split('.')[0]
    out_name = '%s_%s.fits' %(name,extension)
    trigger_name = 'bn%s' % name
    out_file = '%sinput/input_maps/%s' % (GPL_TASKROOT, out_name)
    print(trigger_name, extension, out_name)
    #cmd = 'curl %s -o %s' % (url,out_file)
    #print(cmd)
    #if not os.path.exists(out_file): 
    #os.system(cmd)
    curl_s3df(url, out_file)
    cmd='chmod 777 %s' % out_file
    os.system(cmd)
    #else:
    #    print('File %s already exists' % out_file)
    #    pass
    f=fits.open(out_file)
    date_obs=f[1].header['DATE-OBS'].replace('T',' ')
    met=float(date2met(date_obs))
    print(trigger_name, date_obs, met)
    return trigger_name, out_file, met

if __name__=='__main__':
    __description__='Submit jobs to the GWFUP when data are available...'
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser    = argparse.ArgumentParser(description=__description__,
                                        formatter_class=formatter)
    
    parser.add_argument("--url", help="Web URL of the grace map", type=str, required=False, default=None)
    parser.add_argument("--file", help="Web URL of the grace map", type=str, required=False, default=None)
    parser.add_argument("--version", help="Version number, for multiple excecutions", type=str, default='v01')
    parser.add_argument("--irfs", help="Instrument Response Function", type=str,default='p8_source')
    parser.add_argument("--nside", help="Rescale the MAP to NSIDE", type=int,default=64)
    parser.add_argument("--run_pgwave", help="Run PG wave analysis ONLY", type=bool,default=False)
    parser.add_argument("--run_bayul", help="Run Bayesian UL", type=int,default=1, choices=[0, 1])
    parser.add_argument("--pixels_job", help="Number of pixels per job", type=int,default=5)
    parser.add_argument("--wall_time", help="Pipeline wall time [hours]", type=int, default=4)
    parser.add_argument("--triggername", help="Overwrite the trigger name", type=str, default=None)
    parser.add_argument("--deltatime", help="Overwrite the trigger time by giving the delta", type=int, default=None)
    parser.add_argument("--test", help="Run the script in testing mode", action='store_true')
    parser.add_argument("--force", help="Force the job submission", action='store_true')
    args = parser.parse_args()

    print('GWFUP submitter successfully started on ', datetime.now())
    print('Using %s with PID %s' % (socket.getfqdn(), os.getpid()))
    
    WEB_URL  = args.url
    if WEB_URL is None:
        TRIGGERNAME, HEALPIX_PATH, TRIGGERTIME = getfromfile(args.file)
    else:
        TRIGGERNAME, HEALPIX_PATH, TRIGGERTIME = getfromweb(WEB_URL)
        pass
    VERSION  = args.version
    IRFS     = args.irfs
    NSIDE    = args.nside
    
    if args.triggername is not None:
        TRIGGERNAME = args.triggername
    if args.deltatime is not None:
        TRIGGERTIME += args.deltatime

    _outputdir = '%soutput/%s/%s' % (GPL_TASKROOT, TRIGGERNAME, VERSION)
    while os.path.exists(_outputdir): 
        VNUM = int(VERSION.replace('v', ''))
        VERSION = 'v%02d' % (VNUM+1)
        _outputdir='%soutput/%s/%s' % (GPL_TASKROOT, TRIGGERNAME, VERSION)
        #print('OUTPUT DIRECTORY %s EXISTS!' % _outputdir)
        pass
    
    TSTART    =  0
    TSTOP     =  10000
    FT2TSTART = -10000
    FT2TSTOP  =  TSTOP
    MET_TSTART    = TRIGGERTIME + TSTART
    MET_TSTOP     = TRIGGERTIME + TSTOP
    MET_FT2TSTART = TRIGGERTIME + FT2TSTART
    MET_FT2TSTOP  = TRIGGERTIME + FT2TSTOP
    EMIN   = 100
    EMAX   = 100000
    SIMULATE_MODE = 0
    NUMBER_PIXELS_RUNS = args.pixels_job
    THETAMAX= 65#73 #->65
    ZMAX    = 100 # (DEFAULT=100)
    STRATEGY = 'time' # Don't use event strategy or you will get lots of high TS where the exposure is zero!
    # By setting this var to 1 you will save the .pnz files. Set to 0 if you do not want this!
    BAYESIAN_UL = args.run_bayul
    WALL_TIME = args.wall_time
    
    cmd='%spipeline createStream GWFUP ' % GPL_TASKROOT
    cmd+='--define TRIGGERNAME=%(TRIGGERNAME)s ' % locals()
    cmd+='--define TRIGGERTIME=%(TRIGGERTIME)s ' % locals()
    cmd+='--define MET_TSTART=%(MET_TSTART)s ' % locals()
    cmd+='--define MET_TSTOP=%(MET_TSTOP)s ' % locals()
    cmd+='--define MET_FT2TSTART=%(MET_FT2TSTART)s ' % locals()
    cmd+='--define MET_FT2TSTOP=%(MET_FT2TSTOP)s ' % locals()
    cmd+='--define HEALPIX_PATH=%(HEALPIX_PATH)s ' % locals()
    cmd+='--define EMIN=%(EMIN)s ' % locals()
    cmd+='--define EMAX=%(EMAX)s ' % locals()
    cmd+='--define SIMULATE_MODE=%(SIMULATE_MODE)s ' % locals()
    cmd+='--define NUMBER_PIXELS_RUNS=%(NUMBER_PIXELS_RUNS)s ' % locals()
    cmd+='--define NSIDE=%(NSIDE)s ' % locals()
    cmd+='--define VERSION=%(VERSION)s ' % locals()
    cmd+='--define BAYESIAN_UL=%(BAYESIAN_UL)s ' % locals()
    cmd+='--define IRFS=%(IRFS)s ' % locals()
    cmd+='--define THETAMAX=%(THETAMAX)s ' % locals()
    cmd+='--define ZMAX=%(ZMAX)s ' % locals()
    cmd+='--define STRATEGY=%(STRATEGY)s ' % locals()
    cmd+='--define WALL_TIME=%(WALL_TIME)s:0 ' % locals() # this sets the maximum wall time for the likelihood jobs... format is: H:M
    if args.run_pgwave:
        cmd+='--define RUN_ATI=0 '
        cmd+='--define RUN_FTI=0 '
        cmd+='--define RUN_LLE=0 '
        cmd+='--define RUN_PGW=1 '
        pass

    small_file = '%sstatus/running/%s_%s.txt' % (GPL_TASKROOT, TRIGGERNAME, VERSION)
    if os.path.exists(small_file):
        print('Event %s already running' % TRIGGERNAME)
        sys.exit()
    else:
        txt = cmd.replace('--define','\n --define')
        with open(small_file,'w') as f:
            f.write(txt)
        _cmd ='chmod 777 %s' % small_file
        os.system(_cmd)

    ok = False
    padding = 1000
    t = 0 #hours of waiting
    temp_dir = '%sinput/temp/%s_%s' % (GPL_TASKROOT, TRIGGERNAME, VERSION)
    while not ok:
        ft1, ft2 = download_LAT_data(outdir=temp_dir, ft1='FT1.fits', 
            ft2='FT2.fits', tstart=MET_FT2TSTART, tstop=MET_FT2TSTOP,
            padding=padding, one_sec=False)
        print(ft1)
        print(ft2)
        ok = check_ft1_ft2_files(ft1, ft2, MET_FT2TSTART, 
            MET_FT2TSTOP + padding, patch=500.)
        if ok:
            print('Data look good! Proceeding with the submission now.')
            break
        else:
            print('Not enough data on ', datetime.now())
            if args.force:
                print('WARNING: forcing the job submission anyway.')
                break
            print('Waiting 30 minutes...')
            time.sleep(30*60)
            t += 0.5
        if t > 18:
            print('WARNING: submitter is likely stuck!')
            print('Skipping %s for the moment...' % TRIGGERNAME)
            os.system('rm -rf %s' % temp_dir)
            os.system('mv %s %sstatus/skipped/' % (small_file, GPL_TASKROOT))
            sys.exit()
        # Use the small file to exit the loop and program (if needed)
        if not os.path.exists(small_file):
            print('Submitter was stopped by the user. Exiting now.')
            ok = True
            args.test = True
    os.system('rm -rf %s' % temp_dir)
    
    print('Submitting:')
    print(cmd)
    if args.test == True:
        print('This was a test!')
        os.system('rm %s' % small_file)
    else: 
        os.system(cmd)
        conf_email='mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Job submitted for %s " nicola.omodei@gmail.com <  %s' %(TRIGGERNAME,small_file)
        print(conf_email)
        os.system(conf_email)
        conf_email='mail -r ndilalla@stanford.edu -s "GWFUP Pipeline: Job submitted for %s " ndilalla@stanford.edu <  %s' %(TRIGGERNAME,small_file)
        print(conf_email)
        os.system(conf_email)
        #conf_email='mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Job submitted for %s " o2x6m0g8y0j6y5i7@fermi-lat.slack.com <  %s' %(TRIGGERNAME,small_file)
        #print(conf_email)
        #os.system(conf_email)

