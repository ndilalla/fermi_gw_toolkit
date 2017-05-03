#!/usr/bin/env python

# This script is called by .procmail at Stanford, and receives as standard input the GCN notice


import email
import sys
import os
import logging

try:

    import astropy.io.fits as pyfits

except ImportError:

    import pyfits

from utils import send_email, execute_command

# Configure logger
logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("lvc_notice_parser")
log.setLevel(logging.DEBUG)
log.info('lvc_notice_parser is starting')


if __name__ == "__main__":

    # Parse e-mail message from stdin.

    message = email.message_from_file(sys.stdin)

    # By a pleasant coincidence, Python can parse the colon-separated
    # 'Key: Value' format of GCN notices just like an e-mail header.

    gcn = email.message_from_string(message.get_payload())

    # Filter based on notice type:

    accepted_notice_types = ('TEST LVC Initial Skymap', 'TEST LVC Update Skymap',
                             'LVC Initial Skymap', 'LVC Update Skymap')

    if gcn['NOTICE_TYPE'] in accepted_notice_types and gcn['GROUP_TYPE'] == '1 = CBC':

        # Assemble, echo, and execute curl command to download sky map.
        # NOTE: this will use the username and password stored in .netrc in the user home

        command = "curl --netrc -O '{0}'".format(gcn['SKYMAP_BASIC_URL'])

        try:

            execute_command(log, command)

            # This is like bayestar.fits.gz

            basename = os.path.basename(gcn['SKYMAP_BASIC_URL'])

            # Get the name of the event
            event_name = gcn['TRIGGER_NUM'].replace(" ","")

            # Add "bn" to the name (which is required otherwise some of the scripts might get confused)
            event_name = "bn" + event_name
            
            new_name = '%s_gwmap_%s' % (event_name, basename)
            
            os.rename(basename, new_name)
            
            # Open the FITS file and set the OBJECT keyword if it is not present
            with pyfits.open(new_name, mode='update') as f:
                
                if 'OBJECT' not in f[1].header:
                    
                    f[1].header['OBJECT'] = event_name 

        except:
            status = 'failed'
            raise
        else:

            status = 'success'

        finally:

            text = "Downloaded %s with status: %s" % (gcn['SKYMAP_BASIC_URL'], status)

            log.info(text)

            if gcn['NOTICE_TYPE'].find("TEST") < 0:

                send_email('giacomo.slac@gmail.com', 'LVC NOTICE PROCESSED', text)

    else:

        log.info('Ignoring alert of type %s' % gcn['NOTICE_TYPE'])
