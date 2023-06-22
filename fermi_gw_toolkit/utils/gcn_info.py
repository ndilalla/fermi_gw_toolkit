import gcn
import lxml.etree
import healpy as hp
import json
import urllib
import subprocess

from fermi_gw_toolkit.utils.run_at_slac import run_at_slac

def gracedb_request(url, slac=run_at_slac(), **kwargs):
    if slac:
        try:
            return curl_s3df(url, **kwargs)
        except subprocess.CalledProcessError:
            raise RuntimeError('URL not available')
    else:
        try: 
            return urllib.request.urlopen(url).read()
        except urllib.error.HTTPError:
            raise RuntimeError('URL not available')

def check_url(url):
    try: 
        gracedb_request(url)
        return True
    except RuntimeError:
        return False

def curl_s3df(url, outfile=None, shell=True, text=False, galprop=True):
    #ssh ndilalla@s3dflogin.slac.stanford.edu curl -S https://gracedb.ligo.org/api/superevents/S200316bj/files/bayestar.fits.gz -o - > prova.fits
    #ssh ndilalla@galprop.stanford.edu "source source_gwtable.sh && curl -S https://gracedb.ligo.org/api/superevents/S200316bj/files/bayestar.fits.gz -o -" > prova.fits
    cmd = f'ssh ndilalla@s3dflogin.slac.stanford.edu curl -S {url} -o -'
    if galprop:
        cmd = f'ssh ndilalla@galprop.stanford.edu "source source_gwtable.sh && curl -S {url} -o -"'
    if outfile is not None:
        cmd += f' > {outfile}'
    print('About to run: %s' % cmd)
    return subprocess.check_output(cmd, shell=shell, text=text)

# Function to call every time a GCN is received.
def read_gcn(root, role='observation'):
    if root.attrib['role'] != role:
        return None
    #print(lxml.etree.tostring(root, pretty_print=True))
    # Read all of the VOEvent parameters from the "What" section.
    params = {elem.attrib['name']:
              elem.attrib['value']
              for elem in root.iterfind('.//Param')}
    params['Date'] = root.findtext('.//Date')
    return params

def get_info(name, slac=run_at_slac()):
    url = 'https://gracedb.ligo.org/apiweb/superevents/%s/voevents/?format=json' % name
    try:
        json_url = gracedb_request(url, slac=slac)
        data = json.loads(json_url)
        index = int(data['numRows']) - 1
        xml_url = data['voevents'][index]['links']['file']
        payload = gracedb_request(xml_url, slac=slac)
        root = lxml.etree.fromstring(payload)
        return read_gcn(root)
    except RuntimeError:
        return None

if __name__ == "__main__":
    #name = 'S200116ah'
    name = 'S200114f'
    info = get_info(name)
    print(info)

