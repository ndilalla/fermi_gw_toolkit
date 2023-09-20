import os
import numpy
import healpy
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.lib.local_database import gw_local_database

db_file = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4_events.pkl')
db_dict = gw_local_database.load(db_file)

# file_list = glob('output/*/*/*_results.html')
output_dir = os.path.join(GPL_TASKROOT, 'output')
events_list = sorted(glob('%s/*' % output_dir), reverse=True)

origin = ['BBH', 'BNS', 'NSBH', 'Terrestrial', 'Burst']
bay_ul = []
ati_ts = []
fti_ts = []
astro = []
names = []
ts = []
ul = []
analysis = 'FTI'
plt.figure('Coverage', figsize=(16, 9))

for j, directory in enumerate(events_list[:51]):
    if j % 50 == 0:
        print(j)
    if not os.path.isdir(directory) or not os.listdir(directory):
        continue
    
    name = directory.split('/')[1]
    version = max([i.split('/')[-1][1:3] for i in glob('%s/*' % directory)])

    evt = db_dict['%s/v%s' % (name, version)]

    try:
        copied = evt['Copied']
    except KeyError:
        continue
    bay_ul.append(float(evt['Ene_ul']))
    fti_ts.append(float(evt['Fti_ts']))
    ati_ts.append(float(evt['Ati_ts']))
    if evt['Burst']:
        astro.append('Burst')
    else:
        prob = [float(evt[_key]) for _key in origin[:4]]
        astro.append(str(origin[prob.index(max(prob))]))
    
    if evt['Significant']:
        names.append(name.replace('bn', ''))
        cov_file = os.path.join(directory, version, '%s_coverage.npz' % name)
        sky_coverage = npzfile['cov']
        dt = npzfile['dt']
        plt.plot(dt, sky_coverage, alpha=0.7)

        file_name_ts = '%s_ts_map.fits' % analysis
        file_ts = os.path.join(directory, version, file_name_ts)
        ts_map = healpy.read_map(file_ts)
        ts.append(ts_map[~numpy.isnan(ts_map)])

        file_name_ul = '%s_ul_map.fits' % analysis
        file_ul = os.path.join(directory, version, file_name_ul)
        ul_map = healpy.read_map(file_ul)
        ul.append(ul_map[ul_map > 0])

plt.xlabel("Time since trigger (ks)")
plt.ylabel("Cumulative\nprobability coverage")
plt.ylim([-0.05,1.05])

fig, axes = plt.subplots(num=analysis, nrows=2, ncols=1, figsize=(16, 9), 
                         sharex=True)
axes[0].violinplot(ts, points=100, vert=True, widths=0.8,
                   showmeans=True, showextrema=True, showmedians=False)
#axes[0].set_xticklabels([])
axes[0].xaxis.set_major_locator(MaxNLocator(10))
axes[0].set_ylabel('TS')

axes[1].violinplot(ul, points=100, vert=True, widths=0.8,
                   showmeans=True, showextrema=True, showmedians=False)
axes[1].set_xticklabels([''] + names)
axes[1].xaxis.set_major_locator(MaxNLocator(10))
axes[1].set_yscale('log')
axes[1].set_ylabel('Energy flux upper bounds (erg/cm^2/s)')

astro = numpy.array(astro)

plt.figure('UB')
ul = [numpy.array(bay_ul)[astro == a] for a in origin]
plt.hist(ul, bins=20, label=origin, stacked=True, alpha=0.8)
plt.xlabel('Bayesian UB [erg/cm2/s]')
plt.ylabel('Entries')
plt.legend()

plt.figure('FTI TS')
bins = numpy.linspace(0, 100, 20)
fti = [numpy.array(fti_ts)[astro == a] for a in origin]
plt.hist(fti, bins=bins, label=origin, stacked=True, alpha=0.8)
plt.legend()
plt.xlabel('FTI TS MAX')
plt.ylabel('Entries')

plt.figure('ATI TS')
bins = numpy.linspace(0, 100, 20)
ati = [numpy.array(ati_ts)[astro == a] for a in origin]
plt.hist(ati, bins=bins, label=origin, stacked=True, alpha=0.8)
plt.legend()
plt.xlabel('ATI TS MAX')
plt.ylabel('Entries')

plt.show()