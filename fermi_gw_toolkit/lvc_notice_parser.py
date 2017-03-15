#!/usr/bin/env python

# This script is called by .procmail at Stanford, and receives as standard input the GCN notice

import email
import sys
import subprocess

import smtplib


_message_primitive = """\
From: %s
To: %s
Subject: %s

%s
"""


def send_email(address, subject, msg_text):

    server = "localhost"

    # Yes, I hard-coded this. Putting this in a config. file would be more desirable, but it is way easier to handle
    # a processing script for procmail like this one if it doesn't depend on any external file

    from_field = "giacomov@galprop-cluster.stanford.edu"

    if isinstance(address, list):

        to = address

    else:

        to = [address]  # must be a list

    # Prepare actual message

    msg = _message_primitive % (from_field, ", ".join(to), subject, msg_text)

    # Send the mail

    server = smtplib.SMTP(server)
    server.sendmail(from_field, to, msg)
    server.quit()



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

        print("\nAbout to execute:")
        print(command)

        try:

            subprocess.check_call(command, shell=True)

        except:

            status = 'failed'

        else:

            status = 'success'

        finally:

            text = "Downloaded %s with status: %s" % (gcn['SKYMAP_BASIC_URL'], status)

            send_email('giacomo.slac@gmail.com', 'LVC NOTICE PROCESSED', text)

    else:

        print('Ignoring alert of type %s' % gcn['NOTICE_TYPE'])
