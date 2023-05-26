import os
import json
import numpy as np
import astropy_healpix as ah
from base64 import b64decode
from io import BytesIO
from pprint import pprint
from astropy.table import Table
from gcn_kafka import Consumer
from confluent_kafka import KafkaError

# Connect as a consumer.
# Warning: don't share the client secret with others.
config = {'group.id': 'GWFUP',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'enable.partition.eof': True}

consumer = Consumer(config=config,
                    client_id='1i0tpesjn3drie7jkgup3tvvij',
                    client_secret='1em1btqb3bggvbs1d85v6a9kgt34k7s8vsm5bket1edvsavg0oa1')

def parse_notice(record):
    try:
        record = json.loads(record)

        # Only respond to mock events. Real events have GraceDB IDs like
        # S1234567, mock events have GraceDB IDs like M1234567.
        # NOTE NOTE NOTE replace the conditional below with this commented out
        # conditional to only parse real events.

        # Parse the relevant info
        superevent_id = record['superevent_id']
        alert_type = record['alert_type']
        
        if superevent_id[0] != 'S':
            print(f'{superevent_id} is a test')
            return True
        else:
            print(f'{superevent_id} is a real event')
        
        if alert_type == 'RETRACTION':
            print(f'{superevent_id} was retracted')
            return True
        
        elif alert_type == 'EARLYWARNING' or alert_type == 'PRELIMINARY':
            print(f'Notice for {superevent_id} is still {alert_type}')
            return True

        # Respond only to 'CBC' events. Change 'CBC' to 'Burst' to respond to
        # only unmodeled burst events.
        #if record['event']['group'] != 'CBC':
        #    return

        # Parse sky map
        skymap_str = record.get('event', {}).pop('skymap')
        print('Notice content:')
        pprint(record)
        if skymap_str:
            # Decode, parse skymap, and print most probable sky location
            skymap_bytes = b64decode(skymap_str)
            skymap = Table.read(BytesIO(skymap_bytes))
            mo_skymap_name = '%s_multiorder.fits' % superevent_id
            skymap.write(mo_skymap_name, overwrite=True)
            flat_skymap_name = '%s_flatten.fits.gz' % superevent_id
            
            print('Running ligo-skymap-flatten to get a flat skymap.')
            cmd = 'ligo-skymap-flatten %s %s' % \
                (mo_skymap_name, flat_skymap_name)
            print(cmd)
            os.system(cmd)

            # level, ipix = ah.uniq_to_level_ipix(
            #     skymap[np.argmax(skymap['PROBDENSITY'])]['UNIQ']
            # )
            # ra, dec = ah.healpix_to_lonlat(ipix, ah.level_to_nside(level),
            #                                order='nested')
            # print(f'Most probable sky location (RA, Dec) = ({ra.deg}, {dec.deg})')

            # # Print some information from FITS header
            # print(f'Distance = {skymap.meta["DISTMEAN"]} +/- {skymap.meta["DISTSTD"]}')
            input()
            return True
        else:
            print('WARNING: Skymap not available.')
            return False
    
    except Exception as message:
        print(message)
        return False

# Read the file and then parse it
# with open('MS181101ab-initial.json', 'r') as f:
#     record = f.read()
# parse_notice(record)

# Subscribe to topics and receive alerts
# topics = ['gcn.classic.text.LVC_PRELIMINARY', 'gcn.classic.text.LVC_INITIAL', 'gcn.classic.text.LVC_UPDATE', 'gcn.classic.text.LVC_RETRACTION', 'gcn.classic.text.LVC_UPDATE']
consumer.subscribe(['igwn.gwalert'])

# while True:
    # for message in consumer.consume(timeout=1):
    #     value = message.value()
    #     print(value)
    #     parse_notice(message.value())

test = False
continue_listening = True
while continue_listening == True:
    message = consumer.poll(1)
    if message is None:
        continue
    elif not message.error():
        offset = message.offset()
        print(f"Receiving message #{offset}...")
        commit = parse_notice(message.value())
        if commit == True and test == False: 
            consumer.commit(message)
            print(f"Message #{offset} committed.")
        else:
            print(f'WARNING: Message #{offset} not committed.')
    else:
        continue_listening = False
        if message.error().code() == KafkaError._PARTITION_EOF:
            print("Reached the buffer end.")
        else:
            print(message.error())
        print('Stop listening.')

# Close the consumer before exiting
consumer.close()
print('Consumer closed. Exiting now.')
