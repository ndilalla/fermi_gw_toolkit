import os
import numpy
import healpy
from glob import glob
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.lib.local_database import gw_local_database

o4a_db_file = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4a_events.pkl')
o4a_db_dict = gw_local_database.load(o4a_db_file)
o4a_output_dir = os.path.join(GPL_TASKROOT, 'output', 'rhel6')
o4a_events_list = sorted(glob('%s/*' % o4a_output_dir), reverse=False)

o4b_db_file = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4b_events.json')
o4b_db_dict = gw_local_database.load(o4b_db_file)
o4b_output_dir = os.path.join(GPL_TASKROOT, 'output')
o4b_events_list = sorted(glob('%s/*' % o4b_output_dir), reverse=False)

events_list = o4a_events_list + o4b_events_list
outfile = os.path.join(GPL_TASKROOT, 'databases', 'O4ab_summary.npz')

origin = ['BBH', 'BNS', 'NSBH', 'Terrestrial', 'Burst']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
alpha = 0.7

bay_ul = []
ati_ts_max = []
fti_ts_max = []
astro = []
names = []
ati_ts = []
ati_ul = []
fti_ts = []
fti_ul = []
astro_sign = []
bay_ul_sign = []
t50 = []
t90 = []
cov_1800 = []
cov_3600 = []
cov_5400 = []
cov_max = []

plt.figure('Coverage', figsize=(16, 9))
plt.rc('font', size=16)

for j, directory in enumerate(events_list):
    if j % 50 == 0:
        print(j)
    if not os.path.isdir(directory) or not os.listdir(directory):
        continue
    
    name = directory.split('/')[-1]
    version = 'v%s' % max([i.split('/')[-1][1:3] for i in glob('%s/*' % directory)])
    try:
        if 'rhel6' in directory:
            evt = o4a_db_dict['%s/%s' % (name, version)]
        else:
            evt = o4b_db_dict['%s/%s' % (name, version)]
    except KeyError:
        continue
    try:
        copied = evt['Copied']
        if not copied:
            continue
    except KeyError:
        continue      
    try:
        retracted = evt['Retracted']
        if retracted:
            continue
    except:
        pass
    
    bay_ul.append(float(evt['Ene_ul']))
    fti_ts_max.append(float(evt['Fti_ts']))
    ati_ts_max.append(float(evt['Ati_ts']))
    if evt['Burst']:
        astro.append('Burst')
    else:
        prob = [float(evt[_key]) for _key in origin[:4]]
        astro.append(str(origin[prob.index(max(prob))]))
    
    if (int(evt['Significant'])) == 1:
        names.append(name.replace('bn', ''))
        astro_sign.append(astro[-1])
        bay_ul_sign.append(bay_ul[-1])
        cov_file = os.path.join(directory, version, '%s_coverage.npz' % name)
        npzfile = numpy.load(cov_file)
        sky_coverage = npzfile['cov']
        dt = npzfile['dt']
        plt.plot(dt, sky_coverage, alpha=alpha)

        cov_max.append(sky_coverage.max())
        id50 = numpy.searchsorted(sky_coverage, 0.5)
        if id50 == len(sky_coverage):
            t50.append(10.)
        else:
            t50.append(dt[id50])
        id90 = numpy.searchsorted(sky_coverage, 0.9)
        if id90 == len(sky_coverage):
            t90.append(10.)
        else:
            t90.append(dt[id90])
        cov_1800.append(sky_coverage[numpy.searchsorted(dt, 1.8)])
        cov_3600.append(sky_coverage[numpy.searchsorted(dt, 3.6)])
        cov_5400.append(sky_coverage[numpy.searchsorted(dt, 5.4)])

        file_name_ts = 'FTI_ts_map.fits'
        file_ts = os.path.join(directory, version, file_name_ts)
        ts_map = healpy.read_map(file_ts)
        fti_ts.append(ts_map[~numpy.isnan(ts_map)])

        file_name_ul = 'FTI_ul_map.fits'
        file_ul = os.path.join(directory, version, file_name_ul)
        ul_map = healpy.read_map(file_ul)
        fti_ul.append(ul_map[ul_map > 0])
        
        file_name_ts = 'ATI_ts_map.fits'
        file_ts = os.path.join(directory, version, file_name_ts)
        ts_map = healpy.read_map(file_ts)
        ati_ts.append(ts_map[~numpy.isnan(ts_map)])

        file_name_ul = 'ATI_ul_map.fits'
        file_ul = os.path.join(directory, version, file_name_ul)
        ul_map = healpy.read_map(file_ul)
        ati_ul.append(ul_map[ul_map > 0])

plt.xlabel("Time since trigger (ks)")
plt.ylabel("Cumulative\nprobability coverage")
plt.ylim([-0.05,1.05])
plt.tight_layout()
outfig = outfile.replace('summary.npz', 'coverage.png')
plt.savefig(outfig)

numpy.savez(outfile, bay_ul=numpy.array(bay_ul, dtype=object),
            ati_ts_max=numpy.array(ati_ts_max, dtype=object),
            fti_ts_max=numpy.array(fti_ts_max, dtype=object),
            astro=numpy.array(astro, dtype=object),
            names=numpy.array(names, dtype=object),
            ati_ts=numpy.array(ati_ts, dtype=object),
            ati_ul=numpy.array(ati_ul, dtype=object),
            fti_ts=numpy.array(fti_ts, dtype=object),
            fti_ul=numpy.array(fti_ul, dtype=object),
            astro_sign=numpy.array(astro_sign, dtype=object),
            bay_ul_sign=numpy.array(bay_ul_sign, dtype=object),
            cov_max=numpy.array(cov_max, dtype=object),
            t50=numpy.array(t50, dtype=object),
            t90=numpy.array(t90, dtype=object),
            cov_1800=numpy.array(cov_1800, dtype=object),
            cov_3600=numpy.array(cov_3600, dtype=object),
            cov_5400=numpy.array(cov_5400, dtype=object))

