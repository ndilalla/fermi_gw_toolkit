import smtplib
import sys
import subprocess
import socket
import getpass
import os
from configuration import config
from contextlib import contextmanager

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


def send_notice(subject, text):

    send_email(config.get('EMAIL', 'ERRORS_RECIPIENT'), subject, text)


def fail_with_error(log, error):

    log.error(error)

    send_email(config.get('EMAIL', 'ERRORS_RECIPIENT'), 'LVC PIPELINE FAILURE: ', error)

    sys.exit(-1)


def execute_command(log, cmd_line):

    log.info("About to execute:")
    log.info(cmd_line)

    subprocess.check_call(cmd_line, shell=True)


def sanitize_filename(filename):

    return os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))


@contextmanager
def within_directory(directory, create=False):

    current_dir = os.getcwd()

    directory = sanitize_filename(directory)

    if not os.path.exists(directory):

        if not create:

            raise IOError("Directory %s does not exists!" % os.path.abspath(directory))

        else:

            os.makedirs(directory)

    try:

        os.chdir(directory)

    except OSError:

        raise IOError("Cannot access %s" % os.path.abspath(directory))

    yield

    os.chdir(current_dir)