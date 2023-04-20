import os
from astropy.io import fits as pyfits


def check_ft1_ft2_files(ft1, ft2, tstart, tend, patch=600.0):
    ok = True
    print("Checking FT1 file...")
    if ft1 is None: 
        return False
    if ft2 is None: 
        return False
    if not os.path.exists(ft1): 
        return False
    if not os.path.exists(ft2): 
        return False

    ft1_data = pyfits.open(ft1)['EVENTS'].data
    TIME = ft1_data.TIME
    DT= tend - TIME.max()
    print('TIME range from: %.1f to %.1f' %\
        (TIME.min() - tstart, tend - TIME.max()))
    if DT>patch: 
        print("====> FT1 file probably incomplete. %.1f" % DT)
        ok = False
        os.system('rm -rf %s' % ft1)
    else: 
        print("====> FT1 file complete. %.1f" % DT)
    print("Checking FT2 file...")
    ft2_data = pyfits.open(ft2)[1].data
    STOP = ft2_data.STOP
    DT=tend-STOP.max()
    if DT>patch: 
        print("====> FT2 file probably incomplete. %.1f" % DT)
        ok = False
        os.system('rm -rf %s' % ft2)
    else:
        print("====> FT2 file complete. %.1f" % DT)
    return ok