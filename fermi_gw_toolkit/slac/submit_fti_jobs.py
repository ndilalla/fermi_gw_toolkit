import os
import pipeline

print(dir(pipeline))
print(pipeline.__path__)

print('Opening file %s...' %(OUTLIST))
if os.path.exists(OUTLIST):
    roi_list = open(OUTLIST, 'r')
    rois=roi_list.readlines()
    n_rois=len(rois)
    print('Number of ROI....:',n_rois)
    #n_rois=50
    roi_list.close()
    iStream=0
    """
    while iStream < n_rois:
        if '#' in rois[iStream]:
            iStream+=1
            continue
        ras=''
        decs=''
        for ipixel in range(NUMBER_PIXELS_RUNS):
            if iStream < n_rois:
                ra,dec=rois[iStream].split()
                ras+='%s ' % ra
                decs+='%s ' % dec
                iStream+=1
            if iStream == n_rois: continue
        args='OBJ_RA="%s",OBJ_DEC="%s",SUBDIR="FIXEDINTERVAL",DO_TSMAP="0"' %(ras,decs)
        #print('args=',args)
        pipeline.createSubstream("FTI_Likelihood",iStream+1,args)
    """
else:       
    print('File %s does not exist!' % (OUTLIST))