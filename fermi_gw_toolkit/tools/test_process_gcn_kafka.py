from base64 import b64decode
from io import BytesIO
import json
from pprint import pprint

from astropy.table import Table
import astropy_healpix as ah
from gcn_kafka import Consumer
import numpy as np

# Connect as a consumer.
# Warning: don't share the client secret with others.
#consumer = Consumer(client_id='1i0tpesjn3drie7jkgup3tvvij',
#                    client_secret='1em1btqb3bggvbs1d85v6a9kgt34k7s8vsm5bket1edvsavg0oa1')

def parse_notice(record):
    record = json.loads(record)

    # Only respond to mock events. Real events have GraceDB IDs like
    # S1234567, mock events have GraceDB IDs like M1234567.
    # NOTE NOTE NOTE replace the conditional below with this commented out
    # conditional to only parse real events.

    # Parse the relevant info
    superevent_id = record['superevent_id']
    alert_type = record['alert_type']
    
    # if superevent_id[0] != 'S':
    #    return
    if superevent_id[0] != 'M':
        return
    
    if alert_type == 'RETRACTION':
        print(f'{superevent_id} was retracted')
        return
    
    elif alert_type == 'EARLYWARNING' or alert_type == 'PRELIMINARY':
        print(f'Notice for {superevent_id} is still {alert_type}')
        return

    # Respond only to 'CBC' events. Change 'CBC' to 'Burst' to respond to
    # only unmodeled burst events.
    #if record['event']['group'] != 'CBC':
    #    return
        
    # Parse sky map
    skymap_str = record.get('event', {}).pop('skymap')
    if skymap_str:
        # Decode, parse skymap, and print most probable sky location
        skymap_bytes = b64decode(skymap_str)
        skymap = Table.read(BytesIO(skymap_bytes))
        print(skymap)
        input()

        level, ipix = ah.uniq_to_level_ipix(
            skymap[np.argmax(skymap['PROBDENSITY'])]['UNIQ']
        )
        ra, dec = ah.healpix_to_lonlat(ipix, ah.level_to_nside(level),
                                       order='nested')
        print(f'Most probable sky location (RA, Dec) = ({ra.deg}, {dec.deg})')

        # Print some information from FITS header
        print(f'Distance = {skymap.meta["DISTMEAN"]} +/- {skymap.meta["DISTSTD"]}')

    # Print remaining fields
    print('Record:')
    pprint(record)

# Read the file and then parse it
with open('MS181101ab-initial.json', 'r') as f:
    record = f.read()

parse_notice(record)

# Subscribe to topics and receive alerts
#consumer.subscribe(['igwn.gwalert'])
#while True:
#    for message in consumer.consume(timeout=1):
#        value = message.value()
#        print(value)
#        parse_notice(message.value())
