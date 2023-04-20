import gcn
import lxml.etree
import healpy as hp
import json
import urllib

def check_url(url):
    try: 
        urllib.request.urlopen(url)
        return True
    except urllib.error.HTTPError:
        return False

# Function to call every time a GCN is received.
def read_gcn(payload, root, role='observation'):
    if root.attrib['role'] != role:
        return None

    # Read all of the VOEvent parameters from the "What" section.
    params = {elem.attrib['name']:
              elem.attrib['value']
              for elem in root.iterfind('.//Param')}
    return params

def get_info(name):
    url = 'https://gracedb.ligo.org/apiweb/superevents/%s/voevents/?format=json' % name
    try:
        json_url = urllib.request.urlopen(url)
        data = json.load(json_url)
        index = int(data['numRows']) - 1
        xml_link = data['voevents'][index]['links']['file']
        #print(xml_link)
        payload = urllib.request.urlopen(xml_link).read()
    except urllib.error.HTTPError:
        return None
    
    root = lxml.etree.fromstring(payload)
    return read_gcn(payload, root)

if __name__ == "__main__":
    #name = 'S200116ah'
    name = 'S200114f'
    print(get_info(name))

