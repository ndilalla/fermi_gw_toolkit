import os
import argparse
from astropy.io import fits
from fermi_gw_toolkit.utils.gcn_info import curl_s3df

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)
parser.add_argument("filepath", help="Path to the file to check", type=str)

def check_ligo_map(file_path):
    try:
        ligo_map = fits.open(file_path)
        print('FITS file %s looks good.' % file_path)
    except:
        print('WARNING: FITS file %s looks corrupted!' % file_path)
        print('A second attempt will be made to download it again from GraceDB')
        file_name = os.path.basename(file_path)
        url_base = 'https://gracedb.ligo.org/api/superevents/'
        trigger_name, map_name = file_name.replace('.fits', '').split('_')
        url = os.path.join(url_base, trigger_name, 'files', '%s.fits.gz' %\
                           map_name)
        print('Trying to download from %s' % url)
        curl_s3df(url, outfile=file_path)
        cmd = 'chmod a+r %s' % file_path
        os.system(cmd)
        ligo_map = fits.open(file_path)

if __name__ == '__main__':
    args = parser.parse_args()
    check_ligo_map(args.filepath)
