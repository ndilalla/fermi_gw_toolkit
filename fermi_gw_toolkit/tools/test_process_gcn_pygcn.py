import gcn
import healpy as hp
import lxml.etree
#import ligo.skymap
#import ligo.skymap.io

# Function to call every time a GCN is received.
# Run only for notices of type LVC_EARLY_WARNING, LVC_PRELIMINARY,
# LVC_INITIAL, LVC_UPDATE, or LVC_RETRACTION.
@gcn.handlers.include_notice_types(
    gcn.notice_types.LVC_EARLY_WARNING,
    gcn.notice_types.LVC_PRELIMINARY,
    gcn.notice_types.LVC_INITIAL,
    gcn.notice_types.LVC_UPDATE,
    gcn.notice_types.LVC_RETRACTION)
def process_gcn(payload, root):
    # Respond only to 'test' events.
    # VERY IMPORTANT! Replace with the following code
    # to respond to only real 'observation' events.
    # if root.attrib['role'] != 'observation':
    #    return
    if root.attrib['role'] != 'test':
        return

    # Read all of the VOEvent parameters from the "What" section.
    params = {elem.attrib['name']:
              elem.attrib['value']
              for elem in root.iterfind('.//Param')}

    if params['AlertType'] == 'Retraction':
        print(params['GraceID'], 'was retracted')
        return

    # Respond only to 'CBC' events. Change 'CBC' to 'Burst'
    # to respond to only unmodeled burst events.
    if params['Group'] != 'CBC':
        return

    # Print all parameters.
    for key, value in params.items():
        print(key, '=', value)

    if 'skymap_fits' in params:
        print('Sky map: ', params['skymap_fits'])
        # Read the HEALPix sky map and the FITS header.
        #skymap, header = ligo.skymap.io.read_sky_map(params['skymap_fits'])
        #header = dict(header)

        # Print some values from the FITS header.
        #print('Distance =', header['distmean'], '+/-', header['diststd'])


# Listen for GCNs until the program is interrupted
# (killed or interrupted with control-C).
#gcn.listen(handler=process_gcn)


payload = open('MS181101ab-2-Preliminary.xml', 'rb').read()
root = lxml.etree.fromstring(payload)
process_gcn(payload, root)
