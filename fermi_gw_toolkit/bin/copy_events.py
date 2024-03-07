#!/usr/bin/env python
import os
import urllib
import time
import subprocess
import argparse
import pickle
from glob import glob
from astropy.time import Time
from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.utils.gcn_info import get_info
from fermi_gw_toolkit.utils.slack import send_chat
from fermi_gw_toolkit.lib.local_database import gw_local_database

local_dir = os.path.join(GPL_TASKROOT, 'output')
stanford_dir = '/var/www/html/FermiGRB/GWFUP/'
try:
    _db_file = os.environ['GW_DB_FILE_PATH']
except:
    _db_file = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4b_events.json')

formatter = argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(formatter_class=formatter)
parser.add_argument("--triggername", help="Trigger name", required=False, 
                    default=None, type=str)
parser.add_argument("--version", help="Analysis version", required=False, 
                    default=None, type=str)
parser.add_argument("--directory", help="Path to the 'done' folder", 
                    required=False, default=None, type=str)
parser.add_argument("--db_file", help="File used for database", type=str,
                    required=False, default=_db_file)
#parser.add_argument("--overwrite", )

def fix_html(html, remove=None):
    if not html.endswith('.html'):
        return ''
    with open(html, 'r') as file :
        filedata = file.read()
    if remove is not None:
        filedata = filedata.replace(remove, '')
    filedata = filedata.replace('styles.css', '../../../css/styles.css')
    filedata = filedata.replace('src=PGWAVE', 'src=images/')
    filedata = filedata.replace('src=FIXEDINTERVAL', 'src=images/')
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
    html_path = os.path.join(outfolder, new_name)
    _copy(file_path, outfolder, new_name)
    img_folder = os.path.join(os.path.dirname(file_path), 'images')
    _copy(img_folder, outfolder)
    pgw = os.path.join(os.path.dirname(file_path), 'PGWAVE', '*map.png')
    _copy(pgw, outfolder + '/images/')
    fti =  os.path.join(os.path.dirname(file_path), 'FIXEDINTERVAL', '*map.png')
    _copy(fti, outfolder + '/images/')
    time.sleep(30)
    return html_path

def copy_event(name, db_dict, version=None, overwrite=False, send_alert=True):
    db_update = False
    grace_name = name.replace('bn', '')
    gw_info = get_info(grace_name)
    if gw_info is None:
        # NOT a grace superevent
        print('%s is not a grace superevent' % grace_name)
        return
    
    if version is None:
        version = 'v*'
    res_list = glob('%s/%s/%s/%s_results.html'% (local_dir, name, version, name))
    if len(res_list) == 0:
        # Analysis NOT completed yet
        print('Analysis of %s seems not over yet' % grace_name)
        return
    
    for path in res_list:
        version = os.path.dirname(path).split('/')[-1]
        outfolder = stanford_dir + db_dict.obs_run + '/%s/%s' % (name, version)
        key_event = db_dict.get_key(name, version)

        if not key_event in db_dict:
            db_dict.initialize(grace_name, version)
        
        if not 'Copied' in db_dict[key_event]:
            db_dict.set_value(name, version, 'Copied', False)
        
        if gw_info['AlertType'] == 'Retraction':
            print('%s was retracted' % grace_name)
            db_dict.set_value(name, version, 'Retracted', True)
            if db_dict[key_event]['Copied']:
                # Retracted but already copied
                print('%s has been already copied. Removing now.' % grace_name)
                _rmdir(outfolder)
                db_dict.set_value(name, version, 'Copied', False)
            continue    
        
        if db_dict[key_event]['Copied'] and not overwrite:
            # already copied and NOT overwrite
            print('%s/%s already copied but option set to NOT overwrite' %\
                (grace_name, version))
            continue
        
        print('Copying %s (%s) to Stanford...' % (name, version))
        remove = os.path.join(local_dir, name, version) + '/'
        new_path = fix_html(path, remove)
        html_path = make_copy(new_path, outfolder)
        db_dict.set_value(name, version, 'Copied', True)
    
        db_update = True
        print('Updating the database...')
        if gw_info['Group'] == 'Burst':
            db_dict.update(name, version, 
                {'Burst':True, 'FAR':gw_info['FAR'],\
                 'Significant':gw_info['Significant']})
        else:
            db_dict.set_value(name, version, 'Burst', False)
            if db_dict.obs_run == 'O3':
                _keys = ['FAR', 'BBH', 'BNS', 'NSBH', 'Terrestrial', 'MassGap',\
                        'HasNS', 'HasRemnant']
            else:
                _keys = ['FAR', 'BBH', 'BNS', 'NSBH', 'Terrestrial', \
                         'Significant', 'HasMassGap', 'HasNS', 'HasRemnant']
            _info = {_key:gw_info[_key] for _key in _keys}
            db_dict.update(name, version, _info)
        
        if send_alert:
            ati_ts = float(db_dict.get_value(name, version, "Ati_ts"))
            fti_ts = float(db_dict.get_value(name, version, "Fti_ts"))
            if ati_ts >= 25 or fti_ts >= 25:
                msg = "*Significant detection for %s (%s):*\n\n" %\
                      (name, version)
                msg += "Analysis report: %s\n\n" % html_path
                msg += "Event details:\n %s" % db_dict.dump(name, version)
                print(msg)
                send_chat(msg)

    return db_update

def copy_events(**kwargs):
    name = kwargs['triggername']
    done_dir = kwargs['directory']
    db_file = kwargs['db_file']
    db_dict = gw_local_database.load(db_file)
    db_update = False
    if done_dir is not None:
        files = glob('%s*' % done_dir)
        print('Found %d new events in %s.' % (len(files), done_dir))
        for file_path in files:
            file_name = os.path.basename(file_path).replace('.txt', '')
            name, version = file_name.split('_')
            db_update = copy_event(name, db_dict, version, True) or db_update
            cmd = 'mv %s %s../copied/' % (file_path, done_dir)
            print(cmd)
            os.system(cmd)
    elif name is None:
        print('Trigger name not provided. Looking for new events to copy...')
        files = sorted(glob('%s*' % (local_dir)), reverse=True)
        for directory in files:
            if not os.path.isdir(directory):
                continue
            else:
                name = str(directory).split('/')[-1]
                db_update = copy_event(name, db_dict, send_alert=False) or db_update
    else:
        version = kwargs['version']
        db_update = copy_event(name, db_dict, version, True, False)
    
    #print(db_dict)
    if db_update is True:
        print('Saving the database to %s...' % db_file)
        db_dict.save(db_file)
        _copy(db_file, stanford_dir + db_dict.obs_run + '/')
    print('Done!')

if __name__ == "__main__":
    args = parser.parse_args()
    copy_events(**args.__dict__)

