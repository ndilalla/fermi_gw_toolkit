import os 
import gcn
import healpy as hp
import lxml.etree

from fermi_gw_toolkit import FERMI_GW_ROOT
from fermi_gw_toolkit.utils.gcn_info import read_gcn

# Function to call every time a GCN is received.
# Run only for notices of type, LVC_INITIAL, LVC_UPDATE, or LVC_RETRACTION.
# LVC_EARLY_WARNING, LVC_PRELIMINARY will not trigger the GWFUP pipeline
@gcn.handlers.include_notice_types(
    gcn.notice_types.LVC_INITIAL,
    gcn.notice_types.LVC_UPDATE,
    gcn.notice_types.LVC_RETRACTION)
def process_gcn(payload, root):
    # Read all of the VOEvent parameters
    params = read_gcn(payload, root, role='observation') #'test')
    if params is None:
        return

    if params['AlertType'] == 'Retraction':
        print(params['GraceID'], 'was retracted')
        return

    # Respond only to 'CBC' events. Change 'CBC' to 'Burst'
    # to respond to only unmodeled burst events.
    # if params['Group'] != 'CBC':
    #     return

    # Print all parameters.
    for key, value in params.items():
        print(key, '=', value)

    # Get the sky map url and change it to get the legacy flat resolution map
    # https://gracedb.ligo.org/api/superevents/sid/files/method.multiorder.fits,v
    # https://gracedb.ligo.org/api/superevents/sid/files/method.fits.gz,v
    skymap_url = params['skymap_fits']
    print('Original Multi-Order Sky Map: %s' % skymap_url)
    new_skymap_url = skymap_url.replace('.multiorder.fits', '.fits.gz')
    print('New Flat Resolution Sky Map: %s' % new_skymap_url)

    cmd = 'python %s/tools/submit_gwfup_job.py --url %s --nside 64 --version v01 --run_bayul 0 --pixels_job 5 --wall_time 4 --test' % (FERMI_GW_ROOT, new_skymap_url)
    print(cmd)

    os.system(cmd)

# payload = open('MS181101ab-2-Preliminary.xml', 'rb').read()
# root = lxml.etree.fromstring(payload)
# process_gcn(payload, root)

# Listen for GCNs until the program is interrupted
# (killed or interrupted with control-C).
gcn.listen(handler=process_gcn)