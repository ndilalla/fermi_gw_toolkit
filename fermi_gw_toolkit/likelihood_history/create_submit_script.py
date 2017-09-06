#!/usr/bin/env python

import argparse
import logging
import json
import ConfigParser
import os

from fermi_gw_toolkit.automatic_pipeline.utils import sanitize_filename


logging.basicConfig(format='%(asctime)s %(message)s')

log = logging.getLogger("create_submit_script")
log.setLevel(logging.DEBUG)
log.info('create_submit_script is starting')


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create scripts to be sumbitted to the farm')

    parser.add_argument("--config", help="Configuration file", type=str, required=True)
    parser.add_argument("--gtifile", help="Name of output GTI file (text format)", type=str, required=True)
    parser.add_argument("--scriptfile", help="Output script file (a bash script)", type=str, required=True)

    # parser.add_argument("--package", help="Path to the data package", type=str, required=True)
    parser.add_argument("--outputdir", help="Directory where to store the output results",
                        required=True, type=str)
    parser.add_argument("--n_per_job", help="How many intervals per job", type=int, required=True)

    args = parser.parse_args()

    config_path = sanitize_filename(args.config)

    assert os.path.exists(config_path)

    # package_path = sanitize_filename(args.package)
    #
    # assert os.path.exists(package_path)

    outputdir = sanitize_filename(args.outputdir)

    if not os.path.exists(outputdir):

        os.makedirs(outputdir)

    config = ConfigParser.SafeConfigParser()
    config.read([config_path])

    emin = float(config.get("cuts", "emin"))
    emax = float(config.get("cuts", "emax"))
    irf = config.get("cuts", "irf")

    galactic_model = config.get("likelihood", "galactic_model")
    particle_model = config.get("likelihood", "particle_model")
    tsmin = float(config.get("likelihood", "tsmin"))
    strategy = config.get("likelihood", "strategy")
    ulphindex = config.get("likelihood", "ulphindex")

    gtifile = sanitize_filename(args.gtifile)

    # Open GTI file and read in the cuts and the GTIs
    with open(gtifile) as f:

        spec = json.load(f)

    # Get the logs folder and make sure it exists
    logs_folder = sanitize_filename(config.get("farm", "logs_folder"))

    if not os.path.exists(logs_folder):

        os.makedirs(logs_folder)

    with open(sanitize_filename(args.scriptfile), "w+") as f:

        f.write("#!/bin/bash\n")

        # Find the one_likelihood.py script
        this_path = os.path.dirname(os.path.abspath(__file__))

        one_likelihood_script = os.path.join(this_path, "one_likelihood.py")

        assert os.path.exists(one_likelihood_script)

        for i, (this_starts, this_stops) in enumerate(zip(chunker(spec['starts'], args.n_per_job),
                                           chunker(spec['stops'],  args.n_per_job))):
            cmd_line = "%s " \
                       "--config %s --outputdir %s --tstarts %s --tstops %s" % (one_likelihood_script,
                                                                                config_path,
                                                                                outputdir,
                                                                                ",".join(map(str, this_starts)),
                                                                                ",".join(map(str, this_stops)))


            # Now add the farm submission command
            submit_command = config.get("farm", "submit_command")

            submit_command = submit_command.replace("-LOGS_FOLDER-", logs_folder)

            submit_command = submit_command.replace("-JOBNAME-", "%05i" % (i+1))

            final_cmd_line = "%s %s" % (submit_command, cmd_line)

            f.write("\n%s\n" % final_cmd_line)

