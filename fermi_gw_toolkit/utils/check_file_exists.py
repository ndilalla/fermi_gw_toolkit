__author__ = 'giacomov'

import os


def check_file_exists(filename):

    if os.path.exists(filename):

        return filename

    else:

        raise IOError("Input file %s does not exist!" % filename)
