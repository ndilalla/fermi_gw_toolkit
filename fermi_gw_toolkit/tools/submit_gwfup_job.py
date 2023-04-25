import os
import time
import argparse, glob

from astropy.io import fits
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
    # https://gracedb.ligo.org/api/superevents/S190706ai/fits.gzles/LALInference.offline.fits.gz
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
    __description__='Submitjobs to the GWFUP when data are available...'
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser    = argparse.ArgumentParser(description=__description__,
                                        formatter_class=formatter)
    
    parser.add_argument("--url", help="Web URL of the grace map", type=str, required=False,default=None)
    parser.add_argument("--file", help="Web URL of the grace map", type=str, required=False,default=None)
    parser.add_argument("--version", help="Version number, for multiple excecutions", type=str,default='v01')
    parser.add_argument("--irfs", help="Instrument Response Function", type=str,default='p8_source')
    parser.add_argument("--nside", help="Rescale the MAP to NSIDE", type=int,default=128)
    parser.add_argument("--run_pgwave", help="Run PG wave analysis ONLY", type=bool,default=False)
    parser.add_argument("--run_bayul", help="Run Bayesian UL", type=int,default=0)
    parser.add_argument("--pixels_job", help="Number of pixels per job", type=int,default=10)
    parser.add_argument("--wall_time", help="Pipeline wall time [hours]", type=int, default=2)
    parser.add_argument("--triggername", help="Overwrite the trigger name", type=str, default=None)
    parser.add_argument("--deltatime", help="Overwrite the trigger time by giving the delta", type=int, default=None)
    parser.add_argument("--test", help="Run the script in testing mode", action='store_true')
    args = parser.parse_args()
    
    WEB_URL  = args.url
    if WEB_URL is None:
        TRIGGERNAME,HEALPIX_PATH,TRIGGERTIME = getfromfile(args.file)
    else:
        TRIGGERNAME,HEALPIX_PATH,TRIGGERTIME = getfromweb(WEB_URL)
        pass
    VERSION  = args.version
    IRFS     = args.irfs
    NSIDE    = args.nside
    
    if args.triggername is not None:
        TRIGGERNAME = args.triggername
    if args.deltatime is not None:
        TRIGGERTIME += args.deltatime

    _outputdir='%soutput/%s/%s' % (GPL_TASKROOT, TRIGGERNAME, VERSION)
    while os.path.exists(_outputdir): 
        VNUM=int(VERSION.replace('v',''))
        VERSION='v%02d' % (VNUM+1)
        _outputdir='%soutput/%s/%s' % (GPL_TASKROOT, TRIGGERNAME, VERSION)
        #print('OUTPUT DIRECTORY %s EXISTS!' % _outputdir)
        #exit()
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
    #NUMBER_PIXELS_RUNS = 5#10
    NUMBER_PIXELS_RUNS = args.pixels_job
    THETAMAX= 65#73 #->65
    ZMAX    = 100 # (DEFAULT=100)
    STRATEGY = 'time' # 'events'
    # By setting this var to 1 you will save the .pnz files. Set to 0 if you do not want this!
    BAYESIAN_UL = 0
    if args.run_bayul == 1:
        BAYESIAN_UL = 1
    WALL_TIME = args.wall_time
    
    cmd='./pipeline createStream GWFUP '
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
        print('Event %s already processed' % TRIGGERNAME)
        exit()
        pass    

    ok=False

    temp_dir = '%sinput/temp/%s_%s' % (GPL_TASKROOT, TRIGGERNAME, VERSION)
    while not ok:
        ft1, ft2 = download_LAT_data(**dict(outdir=temp_dir, 
            tstart=MET_FT2TSTART,  tstop=MET_FT2TSTOP, padding=1000, 
            one_sec=False))
        print(ft1)
        print(ft2)
        ok = check_ft1_ft2_files(ft1,ft2,MET_FT2TSTART,MET_FT2TSTOP,patch=600.)
        #ok=True
        if not ok:
            print('Not enough data...')
            print('Wait 5 minutes...')
            time.sleep(5*60)
            #    exit()
            pass
        pass
    os.system('rm -rf %s' % temp_dir)

    outfile=file(small_file,'w')
    outfile.write(cmd)
    outfile.close()
    print('Submitting:')
    print(cmd)
    if args.test == True:
        print('This was a test!')
    else: 
        os.system(cmd)
        conf_email='mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Job submitted for %s " nicola.omodei@gmail.com <  %s' %(TRIGGERNAME,small_file)
        print(conf_email)
        os.system(conf_email)
        conf_email='mail -r ndilalla@stanford.edu -s "GWFUP Pipeline: Job submitted for %s " ndilalla@stanford.edu <  %s' %(TRIGGERNAME,small_file)
        print(conf_email)
        os.system(conf_email)
        txt=cmd.replace('./pipeline createStream GWFUP --define ','')
        txt=txt.replace('--define','\n')
        outfile=file(small_file,'w')
        outfile.write(txt)
        outfile.close()
        #conf_email='mail -r nicola.omodei@gmail.com -s "GWFUP Pipeline: Job submitted for %s " o2x6m0g8y0j6y5i7@fermi-lat.slack.com <  %s' %(TRIGGERNAME,small_file)
        #print(conf_email)
        #os.system(conf_email)

