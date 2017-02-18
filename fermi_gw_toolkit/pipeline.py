#!/usr/bin/env python

from fermi_gw_toolkit.download_LAT_data import download_LAT_data, parser as\
                                                        download_LAT_data_parser
from fermi_gw_toolkit.rawdata2package import rawdata2package, parser as\
                                                        rawdata2package_parser
from fermi_gw_toolkit.prepare_grid import prepare_grid, parser as\
                                                        prepare_grid_parser
from fermi_gw_toolkit.bayesian_ul import bayesian_ul, parser as\
                                                        bayesian_ul_parser
from fermi_gw_toolkit.get_coverage import compute_coverage, parser as\
                                                        get_coverage_parser
from fermi_gw_toolkit.merge_results import merge_results, parser as\
                                                        merge_results_parser
from fermi_gw_toolkit.fill_maps import fill_maps, parser as\
                                                        fill_maps_parser

import os, socket

def run_at_slac():
    """Decide if we are running locally at SLAC or not
    """
    hostname = socket.getfqdn()
    run_at_slac = True
    if hostname.find("slac.stanford.edu") is -1:
        run_at_slac = False
    return run_at_slac

class gwPipeline:

    """Class describing an analysis pipeline for GW follow-up.
    """
    
    def __init__(self, clobber=None):
        """Constructor.
        """
        assert clobber in [None, True, False]
        self.clobber = clobber
        self.run_at_slac = run_at_slac()
    
    def command_line(self, **kwargs):
        """Turn a dictionary into a string that is understood by argparse.
        """
        #if self.clobber is not None:
        #    kwargs['clobber'] = self.clobber
        cmdline = ''
        for key, value in kwargs.items():
            # Need some extra care for lists...
            if isinstance(value, list):
                value = ('%s' % value).replace(' ', '')
            cmdline += '--%s %s ' % (key, value)
        cmdline.strip()
        return cmdline
    
    def download_LAT_data(self, triggername, **kwargs):
        """Download LAT data from the Astro Server.
                
        All command-line switches accepted by download_LAT_data can be passed as
        keyword arguments here.
        """
        switches = self.command_line(**kwargs).split() + [triggername]
        kwargs = download_LAT_data_parser.parse_args(switches).__dict__
        return download_LAT_data(**kwargs)
    
    def rawdata2package(self, **kwargs):
        """Transform an FT1 and an FT2 into a package for gtburst.
        
        All command-line switches accepted by rawdata2package can be passed as
        keyword arguments here.
        """
        switches = self.command_line(**kwargs).split()
        kwargs = rawdata2package_parser.parse_args(switches).__dict__
        return rawdata2package(**kwargs)
    
    def get_coverage(self, **kwargs):
        """Compute the LAT coverage of the LIGO map.
        
        All command-line switches accepted by get_coverage can be passed as
        keyword arguments here.
        """
        switches = self.command_line(**kwargs).split()
        kwargs = get_coverage_parser.parse_args(switches).__dict__
        return compute_coverage(**kwargs)
    
    def prepare_grid(self, **kwargs):
        """Generate a grid to be used for the TS map and the UL map,
        based on the contour of an input probability map in HEALPIX format.
                
        All command-line switches accepted by prepare_grid can be passed as
        keyword arguments here.
        """
        switches = self.command_line(**kwargs).split()
        kwargs = prepare_grid_parser.parse_args(switches).__dict__
        return prepare_grid(**kwargs)
    
    def doTimeResolvedLike(self, triggername, **kwargs):
        """Make the likelihood analysis in the selected roi and time interval.
        
        All command-line switches accepted by doTimeResolvedLike can be passed
        as keyword arguments here.
        """
        cmd = 'python $FERMI_DIR/'
        if not self.run_at_slac:
            cmd += 'lib/'
        cmd += 'python/GtBurst/scripts/doTimeResolvedLike.py %s' %triggername
        for key, value in kwargs.iteritems():
            if key is 'particle_model':
                cmd += (' --%s "%s"') % (str(key), str(value))
            else:
                cmd += (' --%s %s') % (str(key), str(value))
        os.system(cmd)
    
    def bayesian_ul(self, subfolder_dir, **kwargs):
        """Compute a fully-Bayesian upper limit by sampling the posterior
        probability.
                
        All command-line switches accepted by bayesian_ul can be passed as
        keyword arguments here.
        """
        init_dir = os.getcwd()
        print "Changing working directory to: %s" % subfolder_dir
        os.chdir(subfolder_dir)
        switches = self.command_line(**kwargs).split()
        kwargs = bayesian_ul_parser.parse_args(switches).__dict__
        bayesian_ul(**kwargs)
        print "Returning to: %s" % init_dir
        os.chdir(init_dir)
        pass
        
    def merge_results(self, triggername, **kwargs):
        """Merge the txt files containing doTimeResolvedLike results.
                
        All command-line switches accepted by merge_results can be passed as
        keyword arguments here.
        """
        switches = self.command_line(**kwargs).split() + [triggername]
        kwargs = merge_results_parser.parse_args(switches).__dict__
        return merge_results(**kwargs)
        
    def fill_maps(self, **kwargs):
        """Fill the input HEALPIX map with the values taken from the input text
        file.
        
        All command-line switches accepted by fill_maps can be passed as
        keyword arguments here.
        """
        switches = self.command_line(**kwargs).split()
        kwargs = fill_maps_parser.parse_args(switches).__dict__
        return fill_maps(**kwargs)
