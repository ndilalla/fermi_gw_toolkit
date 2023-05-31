import os
import sys
import json
import glob
import socket
import numpy as np
import astropy_healpix as ah
from base64 import b64decode
from io import BytesIO
from pprint import pprint
from astropy.table import Table
from gcn_kafka import Consumer
from confluent_kafka import KafkaError
from datetime import datetime

from fermi_gw_toolkit import FERMI_GW_ROOT, GPL_TASKROOT

skipped_folder = os.path.join(GPL_TASKROOT, 'status', 'skipped')

def parse_notice(record, test=False):
    try:
        record = json.loads(record)

        # Parse the relevant info
        superevent_id = record['superevent_id']
        alert_type = record['alert_type']
        
        if superevent_id[0] != 'S':
            print(f'{superevent_id} is a test.')
            return True
        else:
            print(f'{superevent_id} is a real event.')
        
        if alert_type == 'RETRACTION':
            print(f'{superevent_id} was retracted.')
            return True
        
        elif alert_type == 'EARLYWARNING':
            print(f'Notice for {superevent_id} is still {alert_type}.')
            print('Waiting for Preliminary, Initial or Update notice...')
            return True

        # Respond only to 'CBC' events. Change 'CBC' to 'Burst' to respond to
        # only unmodeled burst events.
        #if record['event']['group'] != 'CBC':
        #    return
        instruments = record['event']['instruments']
        nside = 64
        if len(instruments) < 2:
            nside = 32
        
        if record['event']['group'] != 'Burst' and alert_type == 'PRELIMINARY':
            skipped = glob.glob(skipped_folder)
            file_name = f'{superevent_id}.txt'
            if file_name in skipped:
                print('This is the second Preliminary notice. Starting the analysis.')
                os.system(f'rm {skipped_folder}/{file_name}')
            else:
                print('This is the first Preliminary notice. Waiting the second one before starting the analysis.')
                os.system(f'touch {skipped_folder}/{file_name}')
                return True

        #check and filter if significant / BBH?

        # Parse sky map
        skymap_str = record.get('event', {}).pop('skymap')
        print('Notice content:')
        pprint(record)
        if skymap_str:
            # Decode, parse skymap, and print most probable sky location
            skymap_bytes = b64decode(skymap_str)
            skymap = Table.read(BytesIO(skymap_bytes))
            mo_skymap_name = '%s_multiorder.fits' % superevent_id
            input_dir = os.path.join(GPL_TASKROOT, 'input', 'input_maps')
            mo_skymap_path = os.path.join(input_dir, mo_skymap_name)
            skymap.write(mo_skymap_path, overwrite=True)
            
            flat_skymap_name = '%s_flatten.fits.gz' % superevent_id
            flat_skymap_path = os.path.join(input_dir, flat_skymap_name)

            print('Running ligo-skymap-flatten to get a flat skymap.')
            cmd = 'ligo-skymap-flatten %s %s' % \
                (mo_skymap_path, flat_skymap_path)
            print('About to run: ', cmd)
            os.system(cmd)

            cmd = f'{FERMI_GW_ROOT}/slac/submit_gwfup_job.sh {new_skymap_url} {nside} >> {GPL_TASKROOT}/logs/submit.log'
            print('About to run: ', cmd)
            input()
            if not test:
                os.system(cmd)
            return True
        else:
            print('WARNING: Skymap not available.')
            return False
    
    except Exception as message:
        print(message)
        return False

if __name__=='__main__':
    # Check if the GWFUP pipeline is busy
    status_dir = os.path.join(GPL_TASKROOT, 'status', 'running')
    if len(os.listdir(status_dir)) != 0:
        print('GWFUP pipeline looks busy. Trying again in a bit.')
        sys.exit()

    # Connect as a consumer.
    config = {'group.id': 'GWFUP',
              'auto.offset.reset': 'earliest',
              'enable.auto.commit': False,
              'enable.partition.eof': True}

    consumer = Consumer(config=config,
                        client_id='1i0tpesjn3drie7jkgup3tvvij',
                        client_secret='1em1btqb3bggvbs1d85v6a9kgt34k7s8vsm5bket1edvsavg0oa1')
    consumer.subscribe(['igwn.gwalert'])

    print('GWFUP scheduler successfully started on ', datetime.now())
    print('Using %s with PID %s' % (socket.getfqdn(), os.getpid()))

    test = True
    continue_listening = True
    while continue_listening == True:
        message = consumer.poll(1)
        if message is None:
            continue
        elif not message.error():
            offset = message.offset()
            print(f"Message #{offset} received on ", datetime.now())
            commit = parse_notice(message.value(), test=test)
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
