#!/usr/bin/env python2.7
import os
import urllib2
import time
import subprocess
import argparse
import pickle
from glob import glob
from gcn_info import get_info

decorator = 'http://glast-ground.slac.stanford.edu/Decorator/exp/Fermi/Decorate/groups/grb/GWPIPELINE//'
local_dir = '/nfs/farm/g/glast/u26/GWPIPELINE/output/'
stanford_dir = '/var/www/html/FermiGRB/GWFUP/output/'
dbfile = local_dir + 'db_gw_events.pkl'
def load_dict(infile):
    with open(infile, 'rb') as f:
        _dict = pickle.load(f)
    return _dict
db_dict = load_dict(dbfile)

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)
parser.add_argument("--triggername", help="Trigger name", required=False, 
                    default=None, type=str)
parser.add_argument("--version", help="Analysis version", required=False, 
                    default=None, type=str)
parser.add_argument("--directory", help="Path to the 'done' folder", 
                    required=False, default=None, type=str)
#parser.add_argument("--overwrite", )

def check_url(url):
    try: 
        urllib2.urlopen(url)
        return True
    except urllib2.HTTPError, e:
        return False

def save_dict(_dict, outfile):
    with open(outfile, 'wb') as f:
        pickle.dump(_dict, f)

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
    print 'Executing %s...' % command
    os.system(command)
    raw_input()

def _mkdir(folder):
    command = 'ssh ndilalla@galprop.stanford.edu "mkdir -p %s"' % folder
    print 'Executing %s...' % command
    os.system(command)

def _copy(file_path, outfolder, outname=''):
    command = 'scp -r %s ndilalla@galprop.stanford.edu:%s/%s' %\
        (file_path, outfolder, outname)
    print 'Executing %s...' % command
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

def copy_event(name, version=None, overwrite=False):
    db_update = False
    grace_name = name.replace('bn', '')
    gw_info = get_info(grace_name)
    if gw_info is None:
        # NOT a grace superevent
        print '%s is not a grace superevent' % grace_name
        return
    
    if version is None:
        version = 'v*'
    res_list = glob('%s/%s/%s/%s_results.html'% (local_dir, name, version, name))
    if len(res_list) == 0:
        # Analysis NOT completed yet
        print 'Analysis of %s seems not over yet' % grace_name
        return
    
    for path in res_list:
        version = os.path.dirname(path).split('/')[-1]    
        outfolder = stanford_dir + '%s/%s' % (name, version)
        key_event = "%s/%s" % (name, version)
        if not key_event in db_dict:
            db_dict[key_event] = {'Name':grace_name,
                                  'Version': version}
        
        if not 'Copied' in db_dict[key_event]:
            db_dict[key_event].update({'Copied':False})
        
        if gw_info['AlertType'] == 'Retraction':
            print '%s was retracted' % grace_name
            db_dict[key_event].update({'Retracted':True})
            if db_dict[key_event]['Copied']:
                # Retracted but copied yet
                print '%s has been already copied. Removing now.' % grace_name
                _rmdir(outfolder)
                db_dict[key_event].update({'Copied':False})
            continue    
        if db_dict[key_event]['Copied'] and not overwrite:
            # copied yet and NOT overwrite
            print '%s/%s already copied but NOT set to overwrite' %\
                (grace_name, version)
            continue
        
        print 'Copying %s (%s) to Stanford...' % (name, version)
        remove = decorator + os.path.join('output', name, version) + '/'
        new_path = fix_html(path, remove)
        make_copy(new_path, outfolder)
        db_dict[key_event].update({'Copied':True})
    
        db_update = True
        print 'Updating the database...'
        if gw_info['Group'] == 'Burst':
            db_dict[key_event].update({'Burst':True, 'FAR':gw_info['FAR']})
        else:
            db_dict[key_event].update({'Burst':False})
            _keys = ['FAR', 'BBH', 'BNS', 'NSBH', 'Terrestrial', 'MassGap',
                     'HasNS', 'HasRemnant']
            _info = {_key:gw_info[_key] for _key in _keys}
            db_dict[key_event].update(_info)
    return db_update

def copy_events(**kwargs):
    name = kwargs['triggername']
    done_dir = kwargs['directory']
    db_update = False
    if done_dir is not None:
        files = glob('%s*' % done_dir)
        print 'Found %d new events in %s.' % (len(files), done_dir)
        for file_path in files:
            file_name = os.path.basename(file_path).replace('.txt', '')
            name, version = file_name.split('_')
            db_update = copy_event(name, version, overwrite=True) or db_update
            cmd = 'mv %s %s../copied/' % (file_path, done_dir)
            print cmd
            os.system(cmd)
    elif name is None:
        print 'Trigger name not provided. Looking for new events to copy...'
        files = sorted(glob('%s*' % (local_dir)), reverse=True)
        for directory in files:
            if not os.path.isdir(directory):
                continue
            else:
                name = str(directory).split('/')[-1]
                db_update = copy_event(name) or db_update
    else:
        version = kwargs['version']
        db_update = copy_event(name, version, overwrite=True)
    
    #print(db_dict)
    if db_update is True:
        print 'Saving the database to %s...' % dbfile
        save_dict(db_dict, dbfile)
        _copy(dbfile, stanford_dir)
    print 'Done!'

if __name__ == "__main__":
    args = parser.parse_args()
    copy_events(**args.__dict__)

