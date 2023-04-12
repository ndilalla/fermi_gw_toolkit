#!/usr/bin/env python

from fermi_gw_toolkit.bin.download_LAT_data import download_LAT_data, parser as\
                                                        download_LAT_data_parser
from fermi_gw_toolkit.bin.prepare_grid import prepare_grid, parser as\
                                                        prepare_grid_parser
from fermi_gw_toolkit.bin.AdaptiveTimeIntervals import adaptive_time, parser as\
                                                        adaptive_time_parser
from fermi_gw_toolkit.bin.bayesian_ul import bayesian_ul, parser as\
                                                        bayesian_ul_parser
from fermi_gw_toolkit.bin.get_coverage import compute_coverage, parser as\
                                                        get_coverage_parser
from fermi_gw_toolkit.bin.merge_results import merge_results, parser as\
                                                        merge_results_parser
from fermi_gw_toolkit.bin.fill_maps import fill_maps, parser as\
                                                        fill_maps_parser
from fermi_gw_toolkit import GTBURST_PATH

import os, socket
import glob

def run_at_slac():
    """Decide if we are running locally at SLAC or not
    """
    hostname = socket.getfqdn()
    run_at_slac = True
    if hostname.find("slac.stanford.edu") == -1:
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
    
    def rawdata2package(self, ft1, ft2, triggertime, triggername, ra=0, dec=0, 
                        outdir='.'):
        """Transform an FT1 and an FT2 into a package for gtburst.
        """
        cwd = os.getcwd()
        print("Changing working directory to: %s" % outdir)
        os.chdir(outdir)
        cmd = 'python %s/scripts/rawdata2package.py' % GTBURST_PATH
        cmd += f' {ft1} {ft2} {triggertime} {triggername} {ra} {dec}' % locals()
        os.system(cmd)
        ft1 = glob.glob(outdir + '/gll_ft1_tr_%s_*.fit' % triggername)[0]
        rsp = glob.glob(outdir + '/gll_cspec_tr_%s_*.rsp' % triggername)[0]
        ft2 = glob.glob(outdir + '/gll_ft2_tr_%s_*.fit' % triggername)[0]
        pha = glob.glob(outdir + '/gll_cspec_tr_%s_*.pha' % triggername)[0]
        print("Returning to: %s" % cwd)
        os.chdir(cwd)
        return ft1, rsp, ft2, pha
    
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
    
    def adaptive_time(self, **kwargs):
        """Create a text file with start, stop times and ra-dec coordinates for
        time adaptive interval.
        
        All command-line switches accepted by adaptive_time can be passed as
        keyword arguments here.
        """
        switches = self.command_line(**kwargs).split()
        kwargs = adaptive_time_parser.parse_args(switches).__dict__
        return adaptive_time(**kwargs)
    
    def doTimeResolvedLike(self, triggername, **kwargs):
        """Make the likelihood analysis in the selected roi and time interval.
        
        All command-line switches accepted by doTimeResolvedLike can be passed
        as keyword arguments here.
        """
        cwd = os.getcwd()
        out_dir = os.path.dirname(kwargs.get('outfile', cwd))
        print("Changing working directory to: %s" % out_dir)
        os.chdir(out_dir)
        cmd = 'python %s/scripts/doTimeResolvedLike.py %s' %\
            (GTBURST_PATH, triggername)
        for key, value in kwargs.items():
            if key == 'particle_model':
                cmd += (' --%s "%s"') % (str(key), str(value))
            else:
                cmd += (' --%s %s') % (str(key), str(value))
        try:
            os.system(cmd)
        except:
            pass
        subfolder_dir = os.path.join(out_dir, "interval%s-%s" %\
                        (kwargs.get('tstarts'), kwargs.get('tstops')))
        xml = glob.glob(subfolder_dir + '/*filt_likeRes.xml')[0]
        expomap = glob.glob(subfolder_dir + '/*filt_expomap.fit')[0]
        new_ft1 = glob.glob(subfolder_dir + '/*filt.fit')[0]
        ltcube = glob.glob(subfolder_dir + '/*filt_ltcube.fit')[0]
        print("Returning to: %s" % cwd)
        os.chdir(cwd)
        return subfolder_dir, xml, expomap, new_ft1, ltcube
    
    def bayesian_ul(self, subfolder_dir, **kwargs):
        """Compute a fully-Bayesian upper limit by sampling the posterior
        probability.
                
        All command-line switches accepted by bayesian_ul can be passed as
        keyword arguments here.
        """
        cwd = os.getcwd()
        print("Changing working directory to: %s" % subfolder_dir)
        os.chdir(subfolder_dir)
        switches = self.command_line(**kwargs).split()
        kwargs = bayesian_ul_parser.parse_args(switches).__dict__
        bayesian_ul(**kwargs)
        print("Returning to: %s" % cwd)
        os.chdir(cwd)
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
