import smtplib
import sys
import subprocess
import socket
import getpass
from configuration import config

class DataNotAvailable(RuntimeError):
    pass

_message_primitive = """\
From: %s
To: %s
Subject: %s

%s
"""


def send_email(address, subject, msg_text):

    from_field = "%s@%s" %(getpass.getuser(), socket.getfqdn())

    if isinstance(address, list):

        to = address

    else:

        to = [address]  # must be a list

    # Prepare actual message

    msg = _message_primitive % (from_field, ", ".join(to), subject, msg_text)

    # Send the mail

    server = smtplib.SMTP("localhost")
    server.sendmail(from_field, to, msg)
    server.quit()


def fail_with_error(log, error):

    log.error(error)

    send_email(config.get('EMAIL', 'ERRORS_RECIPIENT'), 'LVC PIPELINE FAILURE: ', error)

    sys.exit(-1)


def execute_command(log, cmd_line):

    log.info("About to execute:")
    log.info(cmd_line)

    subprocess.check_call(cmd_line, shell=True)
