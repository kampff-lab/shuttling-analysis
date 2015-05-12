# -*- coding: utf-8 -*-
"""
Created on Fri May 08 00:36:22 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names,control,lesion,lesionordermap
from activitytables import posturebias, getballistictrials, info_key
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import averagetimeseries, proxylegend
from datapath import jumpers, lesionshamcache, crossings_key
from datapath import crossingactivity_random_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
info = pd.read_hdf(lesionshamcache, info_key)
namemap = lesionordermap(info)
info = info.query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
cr = pd.read_hdf(lesionshamcache,crossings_key).query(nonjumpers)
cract.reset_index('time',inplace=True)

# Select data
bias = 2
group = list(names(info))
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
cr = cr.query(random)
for name in group:
    selection = str.format("subject in {0}",[name])
    scr = cr.query(selection)
    stablebias,unstablebias = posturebias(scr,n=bias)
    stablebias = getballistictrials(stablebias)
    unstablebias = getballistictrials(unstablebias)
    if len(stablebias) == 0 or len(unstablebias) == 0:
        continue
    
    # Select data
    stablebias = stablebias.rename(columns={'index':'crossing'})
    unstablebias = unstablebias.rename(columns={'index':'crossing'})
    stablebias.set_index('crossing',append=True,inplace=True)
    unstablebias.set_index('crossing',append=True,inplace=True)
    scract = cract.join(stablebias,how='inner',rsuffix='R')
    ucract = cract.join(unstablebias,how='inner',rsuffix='R')
    scract.xhead = flipleftwards(scract.xhead,scract.side)
    ucract.xhead = flipleftwards(ucract.xhead,ucract.side)    
    sb_S = scract.query('stepstate3')
    sb_U = scract.query('not stepstate3')
    ub_S = ucract.query('stepstate3')
    ub_U = ucract.query('not stepstate3')
    
    # Plot data    
    name = namemap[name]
    fig, (ax1,ax2) = plt.subplots(1,2)
    colors = ['b','cyan','orange','r']
    averagetimeseries(sb_S,color=colors[0],ax=ax1,alpha=0.25)
    averagetimeseries(sb_U,color=colors[1],ax=ax1,alpha=0.25)
    averagetimeseries(ub_S,color=colors[2],ax=ax1,alpha=0.25)
    averagetimeseries(ub_U,color=colors[3],ax=ax1,alpha=0.25)
    ax1.set_title('average time taken across space')
    ax1.set_ylabel('time (s)')
    ax1.set_ylim(0,3.5)
    averagetimeseries(sb_S,column='yhead',color=colors[0],ax=ax2,alpha=0.25)
    averagetimeseries(sb_U,column='yhead',color=colors[1],ax=ax2,alpha=0.25)
    averagetimeseries(ub_S,column='yhead',color=colors[2],ax=ax2,alpha=0.25)
    averagetimeseries(ub_U,column='yhead',color=colors[3],ax=ax2,alpha=0.25)
    proxylegend(colors,
                ['stable bias [stable]',
                 'stable bias [unstable]',
                 'unstable bias [stable]',
                 'unstable bias [unstable]'],
                ax=ax2,loc='upper left')
    ax2.set_title('average nose trajectory')
    ax2.set_ylabel('nose height (cm)')
    ax2.set_ylim(1,4)
    fig.suptitle(str.format('{0} (n = {1} trials)',name,
                            len(stablebias)+len(unstablebias)))
plt.show()
    
# Save plot
