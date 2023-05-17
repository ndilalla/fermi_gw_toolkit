#!/usr/bin/env python2.7
import os
import urllib
import time
import subprocess
import argparse
import pickle
from glob import glob
from fermi_gw_toolkit import GPL_TASKROOT, DECORATOR_PATH
from fermi_gw_toolkit.utils.gcn_info import get_info
from fermi_gw_toolkit.lib.local_database import gw_local_database

local_dir = os.path.join(GPL_TASKROOT, 'output')
stanford_dir = '/var/www/html/FermiGRB/GWFUP/output/'
try:
    dbfile = os.environ['GW_DB_FILE_PATH']
except:
    dbfile = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4_events.pkl')

# def load_dict(infile):
#     with open(infile, 'rb') as f:
#         _dict = pickle.load(f)
#     return _dict

# def save_dict(_dict, outfile):
#     with open(outfile, 'wb') as f:
#         pickle.dump(_dict, f)

def fix_html(html, remove):
    if not html.endswith('.html'):
        return ''
    with open(html, 'r') as file :
        filedata = file.read()

    filedata = filedata.replace(remove, '')
    filedata = filedata.replace('styles.css', '../../../css/styles.css')
    filedata = filedata.replace('src=PGWAVE', 'src=images/')
    outfile = html.replace('.html', '_fixed.html')
    with open(outfile, 'w') as file:
        file.write(filedata)
    return outfile

def _rmdir(folder):
    command = 'ssh ndilalla@galprop.stanford.edu "rm -rf %s"' % folder
    print('Executing %s...' % command)
    os.system(command)
    raw_input()

def _mkdir(folder):
    command = 'ssh ndilalla@galprop.stanford.edu "mkdir -p %s"' % folder
    print('Executing %s...' % command)
    os.system(command)

def _copy(file_path, outfolder, outname=''):
    command = 'scp -r %s ndilalla@galprop.stanford.edu:%s/%s' %\
        (file_path, outfolder, outname)
    print('Executing %s...' % command)
    os.system(command)

def make_copy(file_path, outfolder):
    _mkdir(outfolder + '/images')
    new_name = os.path.basename(file_path).replace('_fixed.html', '.html')
    _copy(file_path, outfolder, new_name)
    img_folder = os.path.join(os.path.dirname(file_path), 'images')
    _copy(img_folder, outfolder)
    pgw = os.path.join(os.path.dirname(file_path), 'PGWAVE', '*.png')
    _copy(pgw, outfolder + '/images/')
    time.sleep(60)

def copy_events(overwrite=False):
    _files = sorted(glob('%s*' % (local_dir)), reverse=True)
    db_dict = gw_local_database.load(db_file)
    for directory in _files:
        if not os.path.isdir(directory):
            # NOT a directory
            #print('%s is not a directory' % directory)
            continue
        
        name = str(directory).split('/')[-1]
        grace_name = name.replace('bn', '')
        gw_info = get_info(grace_name)
        if gw_info is None:
            # NOT a grace superevent
            print('%s is not a grace superevent' % grace_name)
            continue

        vers_list = glob('%s/v*/%s_results.html'% (directory, name))
        if len(vers_list) == 0:
            # Analysis NOT completed yet
            print('Analysis of %s seems not over yet' % grace_name)
            continue
        
        for path in vers_list:
            version = os.path.dirname(path).split('/')[-1]
            
            outfolder = stanford_dir + '%s/%s' % (name, version)
            key_event = db_dict.get_key(name, version)
            
            if not 'Copied' in db_dict[key_event]:
                #db_dict[key_event].update({'Copied':False})
                db_dict.set_value(name, version, 'Copied', False)

            if gw_info['AlertType'] == 'Retraction':
                print('%s was retracted' % grace_name)
                #db_dict[key_event].update({'Retracted':True})
                db_dict.set_value(name, version, 'Retracted', True)
                if db_dict[key_event]['Copied']:
                    # Retracted but copied yet
                    print('%s has been already copied. Removing now.' %\
                          grace_name)
                    _rmdir(outfolder)
                    #db_dict[key_event].update({'Copied':False})
                    db_dict.set_value(name, version, 'Copied', False)
                continue

            if db_dict[key_event]['Copied'] and not overwrite:
                # copied yet and NOT overwrite
                print('%s already copied but NOT set to overwrite' % grace_name)
                continue
            
            print('Copying %s (%s) to Stanford...' % (name, version))
            remove = os.path.join(DECORATOR_PATH, 'output', name, version) + '/'
            new_path = fix_html(path, remove)
            make_copy(new_path, outfolder)
            #db_dict[key_event].update({'Copied':True})
            db_dict.set_value(name, version, 'Copied', True)
            
            print('Updating the database...')
            if gw_info['Group'] == 'Burst':
                #db_dict[key_event].update({'Burst':True, 'FAR':gw_info['FAR']})
                db_dict.update(name, version, {'Burst':True, \
                                               'FAR':gw_info['FAR']})
            else:
                #db_dict[key_event].update({'Burst':False})
                db_dict.set_value(name, version, 'Burst', False)
                _keys = ['FAR', 'BBH', 'BNS', 'NSBH', 'Noise',\
                         'HasMassGap', 'HasNS', 'HasRemnant']
                _info = {_key:gw_info[_key] for _key in _keys}
                #db_dict[key_event].update(_info)
                db_dict.update(name, version, _info)
            
    #print(db_dict)
    print('Saving the database to %s...' % dbfile)
    db.save(db_file)
    _copy(dbfile, stanford_dir)
    print('Done!')

if __name__ == "__main__":

    #parser = argparse.ArgumentParser()
    #parser.add_argument("directory")
    #args = parser.parse_args()
    copy_events(False)

