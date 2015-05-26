# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:20:47 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names,control,lesion,cagemates,lesionordermap
from activitytables import joinstepactivity, getballistictrials, info_key
from activitytables import normalize, mediannorm, flipleftwards
from activitytables import spatialaverage
from activityplots import boundedcurve
from shuttlingplots import averagetimeseries, createspaceaxis
from shuttlingplots import groupcomparison, proxylegend
from datapath import jumpers, lesionshamcache, crossings_key
from datapath import crossingactivity_random_key, stepfeatures_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
cr = pd.read_hdf(lesionshamcache,crossings_key).query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
cract.reset_index(['subject','session','crossing'],inplace=True)
info = pd.read_hdf(lesionshamcache, info_key)
namemap = lesionordermap(info)
info = info.query(nonjumpers)
info = info.query("subject != 'JPAK_20'")

# Select data
group = list(names(info))
controls = list(names(control(info)))
lesions = list(names(lesion(info)))
matched = list(cagemates(lesion(info)))
selection = str.format("subject in {0}",group)
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
steps = steps.query(random).query(selection)
cr = cr.query(random).query(selection)
steps = joinstepactivity(steps,cr,cract)
steps = getballistictrials(steps)
steps.xhead = flipleftwards(steps.xhead,steps.side)
normalize(steps,mediannorm,['xhead','yhead'],level=['subject'])
steps = steps.rename(columns={'index':'time'})

# Normalize data
cract.reset_index(inplace=True)
cract.set_index(['subject','session','crossing'],inplace=True)
cract = cract.join(steps,how='inner',rsuffix='R')
cract.xhead = flipleftwards(cract.xhead,cract.side)
cract.xhead_speed[cract.side == 'leftwards'] *= -1
bias = cract.eval('xheadR >= 0')
scract = cract[bias]
ucract = cract[~bias]
sb_SA = scract.query('stepstate3')
sb_UA = scract.query('not stepstate3')
ub_SA = ucract.query('stepstate3')
ub_UA = ucract.query('not stepstate3')

# Select data
sts = []
uts = []
fig,(ax1,ax2,ax3) = plt.subplots(1,3)
for selected in group:
    names = [selected]
    selection = str.format("subject in {0}",names)
    sb_S = sb_SA.query(selection)
    sb_U = sb_UA.query(selection)
    ub_S = ub_SA.query(selection)
    ub_U = ub_UA.query(selection)
    
    # Select data
    baseline = slice(0,28)
    xpoints = createspaceaxis()
    st,sterr = spatialaverage(xpoints,pd.concat([sb_S,ub_S]),'xhead_speed',
                              baseline=baseline)
    ut,uterr = spatialaverage(xpoints,pd.concat([sb_U,ub_U]),'xhead_speed',
                              baseline=baseline)
    sts.append(st)
    uts.append(ut)
    
    # Plot data
    if namemap[selected] == 'Ca':
        ax = ax1
    elif namemap[selected] == 'Lb':
        ax = ax2
    else:
        ax = None

    if ax is not None:
        alpha = 0.25
        boundedcurve(xpoints,st,sterr,color='b',ax=ax,alpha=alpha)
        boundedcurve(xpoints,ut,uterr,color='r',ax=ax,alpha=alpha)
        proxylegend(['b','r'],['stable','unstable'],ax=ax,loc='upper left')    
        ax.set_title('average speed across space')
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('speed (cm/s)')
        ax.set_xlim(-15,25)    
        ax.set_ylim(-20,30)
    
#    averagetimeseries(sb_S,'xhead_speed',baseline=baseline,
#                      ax=ax2,color='b',alpha=alpha)
#    averagetimeseries(ub_S,'xhead_speed',baseline=baseline,
#                      ax=ax2,color='orange',alpha=alpha)
#    averagetimeseries(sb_U,'xhead_speed',baseline=baseline,
#                      ax=ax2,color='cyan',alpha=alpha)
#    averagetimeseries(ub_U,'xhead_speed',baseline=baseline,
#                      ax=ax2,color='r',alpha=alpha)
#    ax2.set_title('average speed across space')
#    ax2.set_ylabel('speed (cm/s)')
#    ax2.set_ylim(-20,30)
#    proxylegend(['b','orange','cyan','r'],
#                ['stable [+b]',
#                 'stable [-b]',
#                 'unstable [+b]',
#                 'unstable [-b]'],
#                ax=ax2,loc='upper left')
#    names = [namemap[name] for name in names]
#    title = names if len(names) > 1 else names[0]
#    fig.suptitle(str.format('{0} (n = {1} trials)',title,
#                            len(steps.query(selection))))

# Create data summary
names = [namemap[name] for name in group]
speedup = pd.concat([
    pd.DataFrame.from_items([('speedup',ut-st),('subject',name)])
    for st,ut,name in zip(sts,uts,names)])
speedup = speedup.groupby('subject').sum()
names = speedup.index.to_series()
speedupC = speedup[names.str.startswith('C')]
speedupL = speedup[names.str.startswith('L')]

# Plot data summary
rcParams['figure.figsize'] = 6, 5
groupcomparison([speedupC,speedupL],['b','r'],ax=ax3)
ax3.set_xticks([0,1])
ax3.set_xticklabels(['control','lesion'])
ax3.set_ylabel('speedup (cm/s)')
ax3.set_title('speed profile difference')
plt.tight_layout()
plt.show()

# Save plot
