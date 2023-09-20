IFS=''
read -r -d '' script <<EOF
import os, sys
locals().update(os.environ)
print('Opening file %s...' %(OUTADAPTIVEINTERVALS), file=sys.stderr)
if not os.path.exists(OUTADAPTIVEINTERVALS):
   print('File %s does not exist!' % (OUTADAPTIVEINTERVALS))
else:
    roi_list = open(OUTADAPTIVEINTERVALS, 'r')
    rois=roi_list.readlines()
    n_rois=len(rois)
    print('Number of ROI....:',n_rois, file=sys.stderr)
    roi_list.close()
    #n_rois=50
    iStream=0
    while iStream < n_rois:
        if '#' in rois[iStream]: 
            iStream+=1
            continue
        ras=''
        decs=''
        tstarts=''
        tstops=''
        for ipixel in range(int(NUMBER_PIXELS_RUNS)):
            if iStream < n_rois:
                ra,dec,t0,t1,dt = rois[iStream].split()
                met_tstart=float(t0)+float(TRIGGERTIME)
                met_tstop =float(t1)+float(TRIGGERTIME)
                ras+='%s ' % ra
                decs+='%s ' % dec
                tstarts+='%s ' %  met_tstart
                tstops+='%s ' % met_tstop
                iStream+=1
            if iStream == n_rois:
                continue
        args='OBJ_RA="%s", OBJ_DEC="%s", TSTARTS="%s", TSTOPS="%s", SUBDIR="ADAPTIVEINTERVAL"' %(ras,decs,tstarts,tstops)
        # print('args=',args)
        print("pipelineCreateStream %s %d %s" %("ATI_Likelihood",iStream+1,args))
EOF
python3 -c "$script" | sh
