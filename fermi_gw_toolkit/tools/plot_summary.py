import os
import numpy
import healpy
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FixedLocator
import matplotlib.patches as mpatches

from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.lib.local_database import gw_local_database

outfile = os.path.join(GPL_TASKROOT, 'gw', 'databases', 'O4ab_summary.npz')
output_dir = os.path.join(GPL_TASKROOT, 'output')
events_list = sorted(glob('%s/*' % output_dir), reverse=False)

origin = ['BBH', 'BNS', 'NSBH', 'Terrestrial', 'Burst']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
alpha = (0.5, 0.7)

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
t50 = npzfile['t50']
t90 = npzfile['t90']
cov_1800 = npzfile['cov_1800']
cov_3600 = npzfile['cov_3600']
cov_5400 = npzfile['cov_5400']
cov_max = npzfile['cov_max']

labels=[]
labels.append((mpatches.Patch(color=colors[0], alpha=alpha[0]), origin[0]))
labels.append((mpatches.Patch(color=colors[2], alpha=alpha[0]), origin[2]))
positions = numpy.arange(0, len(names))
vpargs = dict(points=100, positions=positions, vert=True, widths=0.5, 
              showmeans=True, showextrema=True, showmedians=False)

fig, axes = plt.subplots(num='TS FTI vs ATI', nrows=2, ncols=1, 
                         figsize=(16, 9), sharex=True)
vp = axes[0].violinplot(fti_ts, **vpargs)
axes[0].set_ylabel('FTI TS')
axes[0].axhline(25., color='black', linestyle='--')
axes[0].grid(axis='y')
axes[0].legend(*zip(*labels))
c_ = []
for i, pc in enumerate(vp["bodies"]):
    c = colors[origin.index(astro_sign[i])]
    c_.append(c)
    pc.set_color(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha[0])
for partname in ('cbars','cmins','cmaxes','cmeans'):
    vp[partname].set_colors(c_)

vp = axes[1].violinplot(ati_ts, **vpargs)
axes[1].set_ylabel('ATI TS')
axes[1].set_xticks(positions, names, rotation=45, ha='right')
axes[1].axhline(25., color='black', linestyle='--')
axes[1].grid(axis='y')
axes[1].legend(*zip(*labels))
fig.tight_layout()

for i, pc in enumerate(vp["bodies"]):
    pc.set_color(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha[0])
for partname in ('cbars','cmins','cmaxes','cmeans'):
    vp[partname].set_colors(c_)

fig, axes = plt.subplots(num='UB FTI vs ATI', nrows=2, ncols=1, 
                         figsize=(16, 9), sharex=True)

vp = axes[0].violinplot(fti_ul, **vpargs)
axes[0].set_yscale('log')
axes[0].set_ylabel('FTI Energy Flux UB (erg/cm^2/s)')
axes[0].plot(positions, bay_ul_sign, 'vr')
axes[0].legend(*zip(*(labels + [(mpatches.Patch(color='red'), 'Bayesian UB')])), loc=2)
axes[0].grid(axis='y')

for i, pc in enumerate(vp["bodies"]):
    pc.set_color(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha[0])
for partname in ('cbars','cmins','cmaxes','cmeans'):
    vp[partname].set_colors(c_)

vp = axes[1].violinplot(ati_ul, **vpargs)
axes[1].set_xticks(positions, names, rotation=45, ha='right')
axes[1].set_yscale('log')
axes[1].set_ylabel('ATI Energy Flux UB [erg/cm2/s]')
axes[1].legend(*zip(*labels), loc=2)
axes[1].grid(axis='y')
axes[1].set_ylim((5e-11, None))
fig.tight_layout()

for i, pc in enumerate(vp["bodies"]):
    pc.set_color(colors[origin.index(astro_sign[i])])
    pc.set_alpha(alpha[0])
for partname in ('cbars','cmins','cmaxes','cmeans'):
    vp[partname].set_colors(c_)

astro = numpy.array(astro)

plt.figure('UB')
bins = numpy.logspace(-10, -7.5, 25)
ul = [numpy.array(bay_ul)[astro == a] for a in origin]
plt.hist(ul, bins=bins, label=origin, stacked=True, alpha=alpha[1], 
         color=colors)
plt.xlabel('Bayesian UB [erg/cm2/s]')
plt.ylabel('Entries')
plt.legend()
plt.yscale('log')
plt.xscale('log')
plt.grid()
plt.tight_layout()

plt.figure('FTI TS')
bins = numpy.linspace(0, 120, 25)
fti = [numpy.array(fti_ts_max)[astro == a] for a in origin]
plt.hist(fti, bins=bins, label=origin, stacked=True, alpha=alpha[1], 
         color=colors)
plt.legend()
plt.xlabel('FTI TS Max')
plt.ylabel('Entries')
plt.yscale('log')
plt.grid()
plt.tight_layout()

plt.figure('FTI TS 2')
bins = numpy.logspace(0, 4, 30)
fti = [numpy.array(fti_ts_max)[astro == a] for a in origin]
plt.hist(fti, bins=bins, label=origin, stacked=True, alpha=alpha[1], 
         color=colors)
plt.legend()
plt.xlabel('FTI TS Max')
plt.ylabel('Entries')
plt.xscale('log')
plt.yscale('log')
plt.xlim((3, None))
plt.grid()
plt.tight_layout()

plt.figure('ATI TS')
bins = numpy.linspace(0, 100, 21)
ati = [numpy.array(ati_ts_max)[astro == a] for a in origin]
plt.hist(ati, bins=bins, label=origin, stacked=True, alpha=alpha[1], 
         color=colors)
plt.legend()
plt.xlabel('ATI TS Max')
plt.ylabel('Entries')
plt.yscale('log')
plt.grid()
plt.tight_layout()

plt.figure('ATI TS 2')
bins = numpy.logspace(0, 4, 30)
fti = [numpy.array(ati_ts_max)[astro == a] for a in origin]
plt.hist(fti, bins=bins, label=origin, stacked=True, alpha=alpha[1], 
         color=colors)
plt.legend()
plt.xlabel('ATI TS Max')
plt.ylabel('Entries')
plt.xscale('log')
plt.yscale('log')
plt.xlim((3, None))
plt.grid()
plt.tight_layout()

"""
Total / Followed up
        --> Origin
Significant / Non significant

"""
TOTAL = float(1610 + 46 + 6)
FUP = len(bay_ul)
SIGN = len(astro_sign)

def func(pct, allvals):
    absolute = int(numpy.round(pct/100.*numpy.sum(allvals)))
    return f"{pct:.1f}%\n({absolute:d})"

fig, ax = plt.subplots(num='Followed-up')
data = [TOTAL - FUP, FUP]
labels = ['Skipped', 'Followed up']
ax.pie(data, autopct=lambda pct: func(pct, data), labels=labels, 
       textprops=dict(fontsize=13), pctdistance=0.6,
       colors = ['#ff7f0e', '#1f77b4'])
plt.tight_layout()

fig, ax = plt.subplots(num='Origin')
labels, data = numpy.unique(astro, return_counts=True)
#labels, data = labels[[0, 1, 3, 4, 2]], data[[0, 1, 3, 4, 2]]
ax.pie(data, autopct=lambda pct: func(pct, data), labels=labels, 
       textprops=dict(fontsize=13), pctdistance=0.7)
plt.tight_layout()

fig, ax = plt.subplots(num='Significant')
data = [FUP - SIGN, SIGN]
labels = ['Not significant', 'Significant']
ax.pie(data, autopct=lambda pct: func(pct, data), labels=labels, 
       textprops=dict(fontsize=13), pctdistance=0.6, 
       colors=['#2ca02c', '#d62728'])
plt.tight_layout()

fig, ax = plt.subplots(num='Significant origin')
labels, data = numpy.unique(astro_sign, return_counts=True)
ax.pie(data, autopct=lambda pct: func(pct, data), labels=labels, 
       textprops=dict(fontsize=13), pctdistance=0.6)
plt.tight_layout()

plt.figure('T 50')
bins = numpy.linspace(0, 10, 21)
plt.hist(t50, bins=bins)
plt.xlabel('Time 50% Coverage')
plt.ylabel('Entries')
plt.grid()
plt.tight_layout()

plt.figure('T 90')
bins = numpy.linspace(0, 10, 21)
plt.hist(t90, bins=bins)
plt.xlabel('Time 90% Coverage')
plt.ylabel('Entries')
plt.grid()
plt.tight_layout()

plt.figure('Cov Max')
bins = numpy.linspace(0, 1, 21)
plt.hist(cov_max, bins=bins)
plt.xlabel('Maximum Coverage')
plt.ylabel('Entries')
plt.grid()
plt.tight_layout()

plt.figure('Cov 1800')
bins = numpy.linspace(0, 100, 21)
plt.hist(cov_1800 * 100, bins=bins)
plt.xlabel('Coverage after 1.8 ks [%]', size=15)
plt.ylabel('Number of O4a events', size=15)
plt.grid()
plt.tight_layout()
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.figure('Cov 3600')
bins = numpy.linspace(0, 100, 21)
plt.hist(cov_3600 * 100, bins=bins)
plt.xlabel('Coverage after 3.6 ks [%]', size=15)
plt.ylabel('Number of O4a events', size=15)
plt.grid()
plt.tight_layout()
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.figure('Cov 5400')
bins = numpy.linspace(0, 100, 21)
plt.hist(cov_5400 * 100, bins=bins)
plt.xlabel('Coverage after 5.4 ks [%]', size=15)
plt.ylabel('Number of O4a events', size=15)
plt.grid()
plt.tight_layout()
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.show()