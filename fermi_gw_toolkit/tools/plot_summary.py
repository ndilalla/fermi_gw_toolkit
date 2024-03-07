import os
import numpy
import healpy
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FixedLocator
import matplotlib.patches as mpatches

from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.lib.local_database import gw_local_database

db_file = os.path.join(GPL_TASKROOT,'databases', 'db_gw_O4a_events.pkl')
db_dict = gw_local_database.load(db_file)
outfile = os.path.join(GPL_TASKROOT, 'databases', 'O4_summary2.npz')
# file_list = glob('output/*/*/*_results.html')
output_dir = os.path.join(GPL_TASKROOT, 'output')
events_list = sorted(glob('%s/*' % output_dir), reverse=False)

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
cov_max = []

plt.figure('Coverage', figsize=(16, 9))

for j, directory in enumerate(events_list):
    if j % 50 == 0:
        print(j)
    if not os.path.isdir(directory) or not os.listdir(directory):
        continue
    
    name = directory.split('/')[-1]
    version = 'v%s' % max([i.split('/')[-1][1:3] for i in glob('%s/*' % directory)])
    try:
        evt = db_dict['%s/%s' % (name, version)]
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

cov_file = os.path.join(output_dir, 'bnS230922g', 'v02', 'bnS230922g_coverage.npz')
npzfile = numpy.load(cov_file)
sky_coverage = npzfile['cov']
dt = npzfile['dt']
plt.plot(dt, sky_coverage, alpha=alpha)

plt.xlabel("Time since trigger (ks)")
plt.ylabel("Cumulative\nprobability coverage")
plt.ylim([-0.05,1.05])
plt.tight_layout()

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
            cov_3600=numpy.array(cov_3600, dtype=object))
plt.show()
input()

npzfile = numpy.load(outfile, allow_pickle=True)
bay_ul = npzfile['bay_ul']
ati_ts_max = npzfile['ati_ts_max']
fti_ts_max = npzfile['fti_ts_max']
astro = npzfile['astro']
names = npzfile['names']
ati_ts = npzfile['ati_ts']
ati_ul = npzfile['ati_ul']
fti_ts = npzfile['fti_ts']
fti_ul = npzfile['fti_ul']
astro_sign = npzfile['astro_sign']
bay_ul_sign = npzfile['bay_ul_sign']

labels=[]
labels.append((mpatches.Patch(color=colors[0], alpha=alpha), origin[0]))
labels.append((mpatches.Patch(color=colors[2], alpha=alpha), origin[2]))

fig, axes = plt.subplots(num='TS FTI vs ATI', nrows=2, ncols=1, figsize=(16, 9), 
                         sharex=True)
vp = axes[0].violinplot(fti_ts, points=100, vert=True, widths=0.8,
                        showmeans=True, showextrema=True, showmedians=False)
axes[0].set_ylabel('FTI TS')
axes[0].axhline(25., color='black', linestyle='--')
axes[0].grid(axis='y')
axes[0].legend(*zip(*labels))

for i, pc in enumerate(vp["bodies"]):
    pc.set_facecolor(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha)

vp = axes[1].violinplot(ati_ts, points=100, vert=True, widths=0.8,
                        showmeans=True, showextrema=True, showmedians=False)
axes[1].set_ylabel('ATI TS')
axes[1].xaxis.set_major_locator(FixedLocator(numpy.arange(0, len(names))))
axes[1].set_xticklabels(names, rotation=45)
axes[1].axhline(25., color='black', linestyle='--')
axes[1].grid(axis='y')
axes[1].legend(*zip(*labels))
fig.tight_layout()

for i, pc in enumerate(vp["bodies"]):
    pc.set_facecolor(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha)

fig, axes = plt.subplots(num='UB FTI vs ATI', nrows=2, ncols=1, figsize=(16, 9), 
                         sharex=True)

vp = axes[0].violinplot(fti_ul, points=100, vert=True, widths=0.5,
                   showmeans=True, showextrema=True, showmedians=False)
axes[0].set_yscale('log')
axes[0].set_ylabel('FTI Energy flux UB (erg/cm^2/s)')
axes[0].legend(*zip(*labels))
axes[0].plot(numpy.arange(0, len(bay_ul_sign)), bay_ul_sign, 'or')

for i, pc in enumerate(vp["bodies"]):
    pc.set_facecolor(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha)

vp = axes[1].violinplot(ati_ul, points=100, vert=True, widths=0.5,
                        showmeans=True, showextrema=True, showmedians=False)
axes[1].xaxis.set_major_locator(FixedLocator(numpy.arange(1, len(names)+1)))
axes[1].set_xticklabels(names, rotation=45)
axes[1].set_yscale('log')
axes[1].set_ylabel('ATI Energy flux UB (erg/cm^2/s)')
axes[1].legend(*zip(*labels))
fig.tight_layout()

for i, pc in enumerate(vp["bodies"]):
    pc.set_facecolor(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha)

astro = numpy.array(astro)

plt.figure('UB')
ul = [numpy.array(bay_ul)[astro == a] for a in origin]
plt.hist(ul, bins=20, label=origin, stacked=True, alpha=alpha, color=colors)
plt.xlabel('Bayesian UB [erg/cm2/s]')
plt.ylabel('Entries')
plt.legend()
plt.tight_layout()

plt.figure('FTI TS')
bins = numpy.linspace(0, 100, 20)
fti = [numpy.array(fti_ts_max)[astro == a] for a in origin]
plt.hist(fti, bins=bins, label=origin, stacked=True, alpha=alpha, color=colors)
plt.legend()
plt.xlabel('FTI TS MAX')
plt.ylabel('Entries')
plt.tight_layout()

plt.figure('ATI TS')
bins = numpy.linspace(0, 100, 20)
ati = [numpy.array(ati_ts_max)[astro == a] for a in origin]
plt.hist(ati, bins=bins, label=origin, stacked=True, alpha=alpha, color=colors)
plt.legend()
plt.xlabel('ATI TS MAX')
plt.ylabel('Entries')
plt.tight_layout()

plt.show()
