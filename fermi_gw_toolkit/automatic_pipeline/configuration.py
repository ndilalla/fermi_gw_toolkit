import ConfigParser
import os


# Read the configuration from here
configuration_file_path = os.path.join(os.path.dirname(__file__), 'pipeline.conf')

# Parse the config file
config = ConfigParser.SafeConfigParser()
config.read([configuration_file_path])

# Make a quick check that we were actually able to read the file

assert config.has_section('SLAC'), "Could not read configuration file %s" % configuration_file_path