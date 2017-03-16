#!/usr/bin/env python

# This script is called by .procmail at Stanford, and receives as standard input the GCN notice


import email
import sys
import logging
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

        except:

            status = 'failed'

        else:

            status = 'success'

        finally:

            text = "Downloaded %s with status: %s" % (gcn['SKYMAP_BASIC_URL'], status)

            log.info(text)

            send_email('giacomo.slac@gmail.com', 'LVC NOTICE PROCESSED', text)

    else:

        log.info('Ignoring alert of type %s' % gcn['NOTICE_TYPE'])
