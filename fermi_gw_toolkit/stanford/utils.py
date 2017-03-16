import smtplib
import sys
import subprocess

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


def fail_with_error(log, error):

    log.error(error)

    send_email('giacomo.slac@gmail.com', 'FAILED: LVC NOTICE', error)

    sys.exit(-1)


def execute_command(log, cmd_line):

    log.info("About to execute:")
    log.info(cmd_line)

    subprocess.check_call(cmd_line, shell=True)
